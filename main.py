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
        <label>c_user:</label>
        <input type="text" name="c_user" required><br>
        <label>xs:</label>
        <input type="text" name="xs" required><br>
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

def get_access_token(c_user, xs):
    cookies = {
        'c_user': c_user,
        'xs': xs
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        response = requests.get(
            "https://business.facebook.com/business_locations",
            headers=headers,
            cookies=cookies
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
        c_user = request.form['c_user']
        xs = request.form['xs']
        result = get_access_token(c_user, xs)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
