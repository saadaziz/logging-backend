from flask import Flask, request, jsonify, Response, render_template
from models import init_db, insert_log, SessionLocal, Log
from config import JWT_SECRET_KEY, JWT_ISSUER
import jwt
import json
import os
import sys
sys.stdout = sys.stderr

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = Flask(__name__)
init_db()

def validate_auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False, "Unauthorized"

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            audience="logging-service"
        )
        if decoded.get("iss") != JWT_ISSUER:
            return False, "Invalid issuer"
        return True, decoded
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError as e:
        return False, f"Invalid token: {str(e)}"

# --- API Routes ---

@app.route("/log", methods=["POST"])
def write_log():
    is_valid, reason = validate_auth()
    if not is_valid:
        return jsonify({"error": reason}), 401

    data = request.get_json(force=True) or {}
    service = data.get("service")
    level = data.get("level", "INFO")
    message = data.get("message")
    context = data.get("context")

    if not service or not message:
        return jsonify({"error": "Missing required fields"}), 400

    insert_log(service, level, message, json.dumps(context) if context else None)
    return jsonify({"status": "logged"}), 201

@app.route("/logs.json", methods=["GET"])
def get_logs_json():
    session = SessionLocal()
    logs = session.query(Log).order_by(Log.timestamp.desc()).all()
    session.close()

    return jsonify([{
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "service": log.service,
        "level": log.level,
        "message": log.message,
        "context": log.context
    } for log in logs])

@app.route("/logs/download", methods=["GET"])
def download_logs():
    is_valid, reason = validate_auth()
    if not is_valid:
        return jsonify({"error": reason}), 401

    session = SessionLocal()
    logs = session.query(Log).order_by(Log.timestamp.desc()).all()
    session.close()

    output_lines = []
    for log in logs:
        line = f"{log.timestamp} | {log.service} | {log.level} | {log.message} | {log.context}"
        output_lines.append(line)
    content = "\n".join(output_lines)

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=logs.txt"}
    )

@app.route("/logs/purge", methods=["POST"])
def purge_logs():
    is_valid, reason = validate_auth()
    if not is_valid:
        return jsonify({"error": reason}), 401

    session = SessionLocal()
    session.query(Log).delete()
    session.commit()
    session.close()

    return jsonify({"status": "purged"})

# --- UI Route ---

@app.route("/logs", methods=["GET"])
def logs_ui():
    return render_template("logs.html")

# --- Debug / Health ---

@app.route("/ping", methods=["GET"])
def ping():
    return "OK", 200

@app.route("/debug-env")
def debug_env():
    return {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "JWT_ISSUER": os.getenv("JWT_ISSUER")
    }

@app.route("/debug-token", methods=["POST"])
def debug_token():
    token = request.json.get("token")
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], audience="logging-service")
        return jsonify({"valid": True, "claims": decoded})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 401

if __name__ == "__main__":
    app.run(port=5001)
