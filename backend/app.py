from flask import Flask, jsonify, request
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

@app.route("/api/test")
def test():
    import subprocess
    command = request.args.get("command")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return jsonify({"output": result.stdout})
