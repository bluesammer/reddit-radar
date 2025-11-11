from flask import Flask, jsonify, request
from flask_cors import CORS
import praw
import os

app = Flask(__name__)
CORS(app, origins=["https://redditradar.datali.st", "https://lovable.dev", "*"])

# Safe Reddit setup
try:
    reddit = praw.Reddit(
        client_id=os.getenv("client_id"),
        client_secret=os.getenv("client_secret"),
        user_agent=os.getenv("user_agent") or "reddit-radar-bot",
        username=os.getenv("username"),
        password=os.getenv("password")
    )
    reddit.read_only = True
    print("✅ Reddit API initialized successfully")
except Exception as e:
    reddit = None
    print(f"⚠️ Reddit setup failed: {e}")

@app.route("/")
def home():
    return jsonify({"status": "Reddit API connected" if reddit else "Reddit API failed"})

@app.route("/status")
def status():
    return jsonify({"status": "OK", "reddit_ready": reddit is not None})

@app.route("/leads")
def get_leads():
    keywords = request.args.get("keywords", "")
    results = []

    if not reddit:
        return jsonify({"error": "Reddit API not available"}), 500

    try:
        # Broaden search scope
        search_terms = [
            keywords,
            f"{keywords} advice",
            f"{keywords} help",
            f"{keywords} feedback",
            f"how to {keywords}",
        ]

        for term in search_terms:
            for submission in reddit.subreddit("all").search(term, limit=10, sort="new"):
                results.append({
                    "title": submission.title,
                    "url": f"https://www.reddit.com{submission.permalink}",
                    "score": submission.score,
                    "subreddit": submission.subreddit.display_name
                })

        # Remove duplicates (by title)
        seen = set()
        unique_results = []
        for r in results:
            if r["title"] not in seen:
                unique_results.append(r)
                seen.add(r["title"])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"leads": unique_results})




@app.route("/suggest")
def suggest():
    if not reddit:
        return jsonify({"error": "Reddit API not available"}), 500

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
