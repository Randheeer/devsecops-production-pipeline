from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/api/health")
def health():
    return jsonify({
        "status": "UP",
        "service": "backend"
    })

@app.route("/api")
def api():
    return jsonify({
        "message": "DevSecOps API is working",
        "environment": os.getenv("APP_ENV", "development")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
