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
        # Split multiple keywords like "fasting, intermittentfasting"
        terms = [t.strip() for t in keywords.split(",") if t.strip()]
        if not terms:
            terms = ["fasting"]

        for term in terms:
            # Target likely subreddits to keep results relevant
            candidate_subs = [
                "fasting", "intermittentfasting", "waterfasting",
                "FastingScience", "AlternateDayFasting", "DryFasting",
                "Health", "Nutrition"
            ]

            for sub in candidate_subs:
                for submission in reddit.subreddit(sub).search(term, limit=5, sort="new"):
                    title = submission.title.lower()
                    # Filter out spammy content
                    if any(bad in title for bad in ["hire", "discord", "assignment", "essay", "gmail", "homework", "sex"]):
                        continue

                    # Only include posts that actually contain the term in the title
                    if term.lower() not in title:
                        continue

                    results.append({
                        "title": submission.title,
                        "url": f"https://www.reddit.com{submission.permalink}",
                        "score": submission.score,
                        "subreddit": submission.subreddit.display_name
                    })

        # Remove duplicates by URL
        unique = {r["url"]: r for r in results}.values()

        if not unique:
            return jsonify({"leads": [{"title": f"No results found for {keywords}"}]})

        return jsonify({"leads": list(unique)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
