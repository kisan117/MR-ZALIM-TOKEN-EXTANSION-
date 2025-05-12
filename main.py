from flask import Flask, request, render_template_string
import requests
import os

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

        if 'EAAG' in response.text:
            token = "EAAG" + response.text.split('EAAG')[1].split('"')[0]
            return token
        else:
            return "[-] Token not found. Invalid or expired cookies."
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
