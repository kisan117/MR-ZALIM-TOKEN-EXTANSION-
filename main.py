from flask import Flask, request
import requests
import re
import time

app = Flask(__name__)

LOCKED_NAME = "Devil Warriors"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.facebook.com/",
    "Accept-Language": "en-US,en;q=0.9"
}

# Parse full cookie string like: c_user=...; xs=...
def parse_cookie_string(cookie_str):
    cookies = {}
    parts = cookie_str.split(";")
    for part in parts:
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies

def get_fb_dtsg(cookies):
    try:
        res = requests.get("https://www.facebook.com/", cookies=cookies, headers=HEADERS)
        token = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
        return token.group(1) if token else None
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    html = '''
    <h2>Facebook Group Name Lock</h2>
    <form method="POST">
        <input type="text" name="group_uid" placeholder="Enter Group UID" required><br><br>
        <textarea name="cookie" placeholder="Paste your Facebook cookie here (c_user + xs)" required style="width:400px;height:100px;"></textarea><br><br>
        <button type="submit">Lock Group Name</button>
    </form>
    <br>{msg}
    '''
    msg = ""

    if request.method == "POST":
        group_id = request.form.get("group_uid")
        cookie_str = request.form.get("cookie")
        cookies = parse_cookie_string(cookie_str)

        c_user = cookies.get("c_user")
        xs = cookies.get("xs")

        if not c_user or not xs:
            msg = "<p>❌ Cookie missing `c_user` or `xs`. Please paste full cookie.</p>"
        else:
            fb_dtsg = get_fb_dtsg(cookies)
            if not fb_dtsg:
                msg = "<p>❌ fb_dtsg token not found. Cookie might be expired or invalid.</p>"
            else:
                # Get current group name
                res = requests.get(f"https://www.facebook.com/groups/{group_id}", cookies=cookies, headers=HEADERS)
                match = re.search(r'<title>(.*?) \| Facebook</title>', res.text)
                current_name = match.group(1) if match else "Unknown"

                if current_name != LOCKED_NAME:
                    time.sleep(1)

                    graphql_url = "https://www.facebook.com/api/graphql/"
                    payload = {
                        "fb_dtsg": fb_dtsg,
                        "av": c_user,
                        "doc_id": "4744513838980198",
                        "variables": (
                            '{"input":{"group_id":"%s","name":"%s","actor_id":"%s","client_mutation_id":"1"}}'
                            % (group_id, LOCKED_NAME, c_user)
                        )
                    }

                    r = requests.post(graphql_url, headers=HEADERS, cookies=cookies, data=payload)

                    if r.status_code == 200:
                        msg = f"<p><b>✅ Old Name:</b> {current_name}<br><b>New Locked Name:</b> {LOCKED_NAME}</p>"
                    else:
                        msg = f"<p>❌ Update failed:<br>{r.text}</p>"
                else:
                    msg = f"<p><b>✅ Already Locked:</b> {current_name}</p>"

    return html.format(msg=msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
