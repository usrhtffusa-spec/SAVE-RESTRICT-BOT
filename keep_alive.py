# Developer - @usrhtff009
# Channel - https://t.me/usrht01
# Purpose - Professional Keep-alive HTTP server for Cloud Hosting (Render/Railway/Koyeb)

import os
import threading
from flask import Flask, Response

# Initializing Flask App
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    """
    Returns a 200 OK status to the hosting platform's health check.
    """
    return Response("Bot Status: 🟢 Online & Functional", status=200)

def _run():
    # Fetching port from Environment Variables (Default: 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )

def keep_alive():
    """
    Starts the Flask server in a background thread.
    """
    server_thread = threading.Thread(target=_run)
    server_thread.daemon = True
    server_thread.start()

# Optimized for Cloud Deployment
# Developer - @usrhtff009
