
"""
Captcha Python Web Service
Cloud Lab 2, 2026
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from captcha.image import ImageCaptcha
import random
import string
import os

app = Flask(__name__)
CORS(app)

# Create the static folder if it does not exist
os.makedirs("static", exist_ok=True)

# Configuration
CAPTCHA_TEXT_LENGTH = 6

# Store the current CAPTCHA answer for this lab
current_captcha_answer = None


def generate_random_text():
    """Generate six uppercase letters and digits."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=CAPTCHA_TEXT_LENGTH))


@app.route("/")
def index():
    """Display the frontend page."""
    return render_template("index.html")


@app.route("/captcha", methods=["GET"])
def get_captcha():
    """Generate a new CAPTCHA and save its image."""
    global current_captcha_answer

    current_captcha_answer = generate_random_text()

    image = ImageCaptcha(width=280, height=90)
    image.write(current_captcha_answer, "static/captcha.png")

    return jsonify({
        "status": "generated",
        "message": "New CAPTCHA image created",
        "debug_text": current_captcha_answer
    }), 200


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve files from the static folder."""
    return send_from_directory("static", filename)


@app.route("/verify", methods=["POST"])
def verify_captcha():
    """Check the user's CAPTCHA answer."""
    if current_captcha_answer is None:
        return jsonify({
            "status": "failed",
            "reason": "Please generate a CAPTCHA first"
        }), 400

    data = request.get_json(silent=True)

    if not data or not isinstance(data.get("captcha"), str):
        return jsonify({
            "error": "Missing or invalid 'captcha' value"
        }), 400

    user_input = data["captcha"].strip().upper()

    if user_input == current_captcha_answer:
        return jsonify({"status": "verified"}), 200

    return jsonify({
        "status": "failed",
        "reason": "Incorrect text"
    }), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("CAPTCHA Service Running...")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
