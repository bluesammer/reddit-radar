from flask import Flask, jsonify, request
from flask_cors import CORS
import praw
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*", "https://redditradar.datali.st", "https://lovable.dev", "http://localhost:5173"]}})

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

@app.route("/")
def home():
    return jsonify({"status": "Reddit API connected"})

@app.route("/status")
def status():
    return jsonify({"status": "Reddit API connected"})



@app.route("/subreddit/<name>")
def get_subreddit_posts(name):
    posts = []
    try:
        for submission in reddit.subreddit(name).hot(limit=5):
            posts.append({
                "title": submission.title,
                "score": submission.score,
                "url": submission.url,
                "author": str(submission.author),
                "created_utc": submission.created_utc
            })
        return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/suggest")
def suggest():
    query = request.args.get("query", "")
    subreddits = set()
    try:
        for submission in reddit.subreddit("all").search(query, limit=10):
            subreddits.add(submission.subreddit.display_name)
        return jsonify({"subreddits": list(subreddits)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
