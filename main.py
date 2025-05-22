from flask import Flask, request
import requests
import re
import time

app = Flask(__name__)

LOCKED_NAME = "Devil Warriors"

COOKIES = {
    "c_user": "YOUR_C_USER",     # e.g., '100012345678901'
    "xs": "YOUR_XS_TOKEN"        # e.g., '34%:abc123...'
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.facebook.com/",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_fb_dtsg():
    res = requests.get("https://www.facebook.com/", cookies=COOKIES, headers=HEADERS)
    token = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
    return token.group(1) if token else None

@app.route("/", methods=["GET", "POST"])
def index():
    html = '''
    <h2>Facebook Group Name Lock (Graph Internal)</h2>
    <form method="POST">
        <input type="text" name="group_uid" placeholder="Enter Group UID" required>
        <button type="submit">Lock Group Name</button>
    </form>
    {msg}
    '''
    msg = ""
    if request.method == "POST":
        group_id = request.form.get("group_uid")
        fb_dtsg = get_fb_dtsg()

        if not fb_dtsg:
            msg = "<p>❌ fb_dtsg token not found. Check your cookies.</p>"
        else:
            # Step 1: Get current group name (just HTML title)
            res = requests.get(f"https://www.facebook.com/groups/{group_id}", cookies=COOKIES, headers=HEADERS)
            match = re.search(r'<title>(.*?) \| Facebook</title>', res.text)
            current_name = match.group(1) if match else "Unknown"

            if current_name != LOCKED_NAME:
                time.sleep(1)

                # Step 2: GraphQL mutation (internal)
                graphql_url = "https://www.facebook.com/api/graphql/"
                payload = {
                    "fb_dtsg": fb_dtsg,
                    "av": COOKIES["c_user"],
                    "doc_id": "4744513838980198",  # This ID is for group name update (may change)
                    "variables": (
                        '{"input":{"group_id":"%s","name":"%s","actor_id":"%s","client_mutation_id":"1"}}'
                        % (group_id, LOCKED_NAME, COOKIES["c_user"])
                    )
                }

                r = requests.post(graphql_url, headers=HEADERS, cookies=COOKIES, data=payload)

                if r.status_code == 200:
                    msg = f"<p><b>✅ Old Name:</b> {current_name}<br><b>New Locked Name:</b> {LOCKED_NAME}</p>"
                else:
                    msg = f"<p>❌ Update failed: {r.text}</p>"
            else:
                msg = f"<p><b>✅ Already Locked:</b> {current_name}</p>"

    return html.format(msg=msg)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
