from flask import Flask, render_template, request, redirect, url_for
import json
import time
import os

app = Flask(__name__)

LOG_PATH = "logs/ratings.jsonl"
ASSET_PATH = "static/generated.png"

# This function is called by your diffusion pipeline
# to update the current asset being reviewed.
def save_new_asset(image_bytes):
    with open(ASSET_PATH, "wb") as f:
        f.write(image_bytes)

@app.route("/")
def index():
    # Force browser to reload the image by adding a timestamp
    ts = int(time.time())
    return render_template("index.html", ts=ts)

@app.route("/rate", methods=["POST"])
def rate():
    rating = request.form.get("rating")  # "reject", "1", "2", "3", "4"

    entry = {
        "timestamp": time.time(),
        "rating": rating,
        "asset_path": ASSET_PATH,
        # Add any metadata you want:
        "seed": request.form.get("seed"),
        "traits": request.form.get("traits"),
        "username": request.form.get("username"),
        "emoji_sequence": request.form.get("emoji_sequence")
    }

    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # After rating, redirect back to main page
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
