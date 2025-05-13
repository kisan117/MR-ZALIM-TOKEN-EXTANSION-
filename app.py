
from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

HTML = """
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
"""

def get_access_token_with_playwright(combined_cookie):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            cookie_list = []
            cookies = combined_cookie.split(';')
            for cookie in cookies:
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    cookie_list.append({
                        'name': name,
                        'value': value,
                        'domain': '.facebook.com',
                        'path': '/',
                        'httpOnly': False,
                        'secure': True
                    })

            context.add_cookies(cookie_list)
            page = context.new_page()
            page.goto("https://business.facebook.com/business_locations", timeout=60000)

            content = page.content()
            browser.close()

            if "EAAB" in content:
                token = "EAAB" + content.split("EAAB")[1].split('"')[0]
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
        result = get_access_token_with_playwright(combined_cookie)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
