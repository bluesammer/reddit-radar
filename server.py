from flask import Flask, jsonify, request
from flask_cors import CORS
import praw
import os

app = Flask(__name__)
CORS(app, origins=["https://redditradar.datali.st", "https://lovable.dev", "*"])

# Reddit API setup
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

# Suggest subreddits for a given query
@app.route("/suggest")
def suggest():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    results = []
    try:
        for subreddit in reddit.subreddits.search(query, limit=10):
            results.append({
                "name": subreddit.display_name,
                "title": subreddit.title,
                "subscribers": subreddit.subscribers
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"suggestions": results})

# Fetch recent leads (posts matching a keyword)
@app.route("/leads")
def leads():
    keywords = request.args.get("keywords", "")
    if not keywords:
        return jsonify({"error": "Missing keywords"}), 400

    posts = []
    try:
        for submission in reddit.subreddit("all").search(keywords, limit=10):
            posts.append({
                "title": submission.title,
                "url": f"https://reddit.com{submission.permalink}",
                "score": submission.score,
                "subreddit": submission.subreddit.display_name
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(posts)

# Create simple message outline for outreach
@app.route("/message-outline")
def message_outline():
    post_id = request.args.get("post_id")
    if not post_id:
        return jsonify({"error": "Missing post_id"}), 400

    try:
        post = reddit.submission(id=post_id)
        outline = f"Hi, I saw your post '{post.title}' in r/{post.subreddit}. I think our tool could help with that!"
        return jsonify({"outline": outline})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
