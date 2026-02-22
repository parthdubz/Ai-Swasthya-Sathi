from flask import Flask, jsonify, Response
from flask_cors import CORS
from supabase import create_client
import requests   # ⭐ ADD THIS ⭐

SUPABASE_URL = "ENTER YOUR URL"
SUPABASE_KEY = "ENTER YOUR KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

# -------------------------------
# Existing Symptoms Endpoint
# -------------------------------
@app.route("/symptoms")
def symptoms():
    res = (
        supabase
        .table("symptoms_log")
        .select("time, symptom")
        .order("time", desc=True)
        .limit(20)
        .execute()
    )
    return jsonify(res.data)

# -------------------------------
# NEW: WHO NEWS ENDPOINT
# -------------------------------
@app.route("/who-news")
def who_news():
    try:
        url = "https://www.who.int/rss-feeds/news-english.xml"
        response = requests.get(url, timeout=5)

        return Response(
            response.content,
            content_type="application/xml"
        )
    except Exception as e:
        return jsonify({"error": "Failed to fetch WHO news"}), 500

# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
