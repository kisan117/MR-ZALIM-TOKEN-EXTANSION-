from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1c1c1c; color: #fff; padding: 30px; }
        form { background: #2c2c2c; padding: 20px; border-radius: 10px; width: 400px; margin: auto; }
        input[type=text], input[type=submit] {
            width: 100%%; padding: 10px; margin: 10px 0;
            border: none; border-radius: 5px;
        }
        input[type=submit] { background: #4CAF50; color: white; cursor: pointer; }
        .result { background: #333; padding: 15px; margin-top: 20px; border-radius: 10px; }
    </style>
</head>
<body>
    <h2>Facebook Real Token Extractor</h2>
    <form method="POST">
        <label>Enter combined c_user and xs cookies:</label>
        <input type="text" name="cookies" required><br>
        <input type="submit" value="Get Token">
    </form>
    {% if result %}
        <div class="result">
            <strong>Result:</strong>
            <pre>{{ result }}</pre>
        </div>
    {% endif %}
</body>
</html>
'''

def get_access_token(combined_cookie):
    try:
        # Split the combined cookie string into individual cookies
        cookies_dict = {}
        cookies = combined_cookie.split(';')
        
        for cookie in cookies:
            # Remove leading/trailing spaces and split cookie name and value
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies_dict[name] = value
        
        # Extract c_user and xs from cookies_dict
        c_user = cookies_dict.get('c_user', None)
        xs = cookies_dict.get('xs', None)

        # Validate if we have both cookies
        if not c_user or not xs:
            return "[-] Missing c_user or xs in cookies."
        
        # Get first 15 characters from c_user and xs
        c_user = c_user[:15]  # Get first 15 characters
        xs = xs[:15]          # Get first 15 characters

        # Set cookies for request
        cookie_data = {
            'c_user': c_user,
            'xs': xs
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        # Make request to Facebook's business page to check validity of cookies
        response = requests.get(
            "https://business.facebook.com/business_locations",
            headers=headers,
            cookies=cookie_data
        )

        # Check if the response contains EAAB
        if 'EAAB' in response.text:
            token = "EAAB" + response.text.split("EAAB")[1].split('"')[0]
            return token
        else:
            return "[-] EAAB Token not found. Invalid or expired cookies."
    except Exception as e:
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        combined_cookie = request.form['cookies']
        result = get_access_token(combined_cookie)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
