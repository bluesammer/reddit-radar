from flask import Flask, jsonify, request
import praw
import os

app = Flask(__name__)

reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

@app.route("/")
def home():
    return {"status": "Reddit API connected"}

@app.route("/subreddit/<name>")
def get_subreddit_posts(name):
    posts = []
    for submission in reddit.subreddit(name).hot(limit=5):
        posts.append({
            "title": submission.title,
            "score": submission.score,
            "url": submission.url
        })
    return jsonify(posts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
