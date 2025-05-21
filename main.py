import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

def extract_c_user_xs(cookie_string):
    cookies = {}
    parts = [p.strip() for p in cookie_string.replace('\n', ';').split(';') if p.strip()]
    for part in parts:
        if '=' in part:
            key, val = part.split('=', 1)
            cookies[key.strip()] = val.strip()
    return cookies.get('c_user'), cookies.get('xs')

def get_eaab_token(c_user, xs):
    cookie_header = f"c_user={c_user}; xs={xs};"
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    url = "https://business.facebook.com/business_locations"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        start = html.find('EAAB')
        if start == -1:
            return None
        eaab_token = html[start:start + 200].split('"')[0]
        return eaab_token
    except Exception as e:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    eaab_token = ''
    if request.method == 'POST':
        cookie_string = request.form.get('cookies')
        c_user, xs = extract_c_user_xs(cookie_string)
        if c_user and xs:
            eaab_token = get_eaab_token(c_user, xs)
            if eaab_token:
                message = "EAAB Token extracted successfully!"
            else:
                message = "EAAB Token not found. Check your cookies or try again."
        else:
            message = "c_user or xs cookie missing in your input!"

    return render_template_string('''
        <h2>Facebook EAAB Token Extractor</h2>
        <form method="post">
            <label>Paste your Facebook cookies (including c_user and xs):</label><br>
            <textarea name="cookies" rows="6" cols="60" placeholder="c_user=...; xs=...;"></textarea><br><br>
            <button type="submit">Get EAAB Token</button>
        </form>
        <p style="color:green;"><b>{{message}}</b></p>
        {% if eaab_token %}
            <label>Your EAAB Token:</label><br>
            <textarea rows="4" cols="60" readonly>{{eaab_token}}</textarea>
        {% endif %}
    ''', message=message, eaab_token=eaab_token)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
