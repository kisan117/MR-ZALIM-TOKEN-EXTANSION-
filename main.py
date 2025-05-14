from flask import Flask, request, render_template_string
import requests
import random
import time
from threading import Thread

app = Flask(__name__)

# ====== CONFIG ======
GROUP_ID = "YOUR_GROUP_ID"
ACCESS_TOKEN = "YOUR_LONG_LIVED_ACCESS_TOKEN"
BOT_NAME = "Devil Bot"

# ==== Funny Replies ====
funny_replies = [
    "Oye hoye, kya sawaal puchha!",
    "Mujhe sochne do... ya nahi, mazaak hi theek hai!",
    "Yeh to rocket science lag raha hai!",
    "Tera sawaal sunke AI bhi hil gaya!",
    "Matlab hadd hi ho gayi bhai!"
]

# ==== Group Name Options ====
def get_group_name_options():
    return ["Chill Zone", "Fun Adda 2.0", "Bakwaas Mandli"]

# ==== Get Latest Comments ====
def get_latest_posts():
    url = f"https://graph.facebook.com/{GROUP_ID}/feed"
    params = {"access_token": ACCESS_TOKEN}
    res = requests.get(url, params=params).json()
    return res.get("data", [])

# ==== Comment Back ====
def comment_on_post(post_id, message):
    url = f"https://graph.facebook.com/{post_id}/comments"
    data = {"message": message, "access_token": ACCESS_TOKEN}
    requests.post(url, data=data)

# ==== Change Group Name ====
def change_group_name(new_name):
    url = f"https://graph.facebook.com/{GROUP_ID}"
    data = {"name": new_name, "access_token": ACCESS_TOKEN}
    res = requests.post(url, data=data)
    return res.json()

# ==== Main Webpage Route ====
@app.route("/", methods=["GET", "POST"])
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Devil Bot</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f7f7f7; }
            h1 { color: #333; }
            .reply, .options { margin-top: 20px; padding: 10px; background: #fff; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h1>Devil Bot - Facebook Group Fun Bot</h1>
        <form method="POST">
            <input type="text" name="user_message" placeholder="Type something like 'bot hello'" required>
            <button type="submit">Send</button>
        </form>
        {% if reply %}
        <div class="reply"><strong>Bot Reply:</strong> {{ reply }}</div>
        {% endif %}
        {% if show_options %}
        <div class="options">
            <form method="POST">
                <p><strong>Select a new group name:</strong></p>
                {% for option in options %}
                <label><input type="radio" name="group_name" value="{{ option }}"> {{ option }}</label><br>
                {% endfor %}
                <button type="submit">Change Group Name</button>
            </form>
        </div>
        {% endif %}
    </body>
    </html>
    '''

    if request.method == "POST":
        if "group_name" in request.form:
            new_name = request.form["group_name"]
            change_group_name(new_name)
            return render_template_string(html, reply=f"Group name changed to: {new_name}", show_options=False)

        user_message = request.form["user_message"].lower()
        if "change the group name" in user_message:
            return render_template_string(html, show_options=True, options=get_group_name_options())
        elif "bot" in user_message:
            return render_template_string(html, reply=random.choice(funny_replies), show_options=False)

    return render_template_string(html, show_options=False)

# ==== Background Bot Function ====
def run_bot():
    print("Bot is running in background...")
    seen_posts = set()

    while True:
        try:
            posts = get_latest_posts()
            for post in posts:
                post_id = post['id']
                message = post.get('message', '')

                if post_id in seen_posts:
                    continue

                if "bot" in message.lower() or "change the group name" in message.lower():
                    if "change the group name" in message.lower():
                        options = get_group_name_options()
                        comment = f"Select new group name:\n1. {options[0]}\n2. {options[1]}\n3. {options[2]}"
                        comment_on_post(post_id, comment)
                    else:
                        comment_on_post(post_id, random.choice(funny_replies))

                seen_posts.add(post_id)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(10)

# ==== Start Everything ====
if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
