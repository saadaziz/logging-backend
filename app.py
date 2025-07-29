from flask import Flask, request, jsonify, Response
from models import init_db, insert_log, SessionLocal, Log
from config import SERVICE_KEY
import json
import sys

app = Flask(__name__)
init_db()

# Log the key loaded at startup
print(f"[DEBUG] SERVICE_KEY loaded at startup: '{SERVICE_KEY}'", file=sys.stderr)

#@app.route("/debug-env")
#def debug_env():
#    import os
#    return {k: v for k, v in os.environ.items() if "KEY" in k or "LOG" in k}

#@app.route("/debug-key", methods=["GET"])
#def debug_key():
#    import os
#    return {"LOG_SERVICE_KEY": os.getenv("LOG_SERVICE_KEY")}

# --- Helper for Auth ---
def check_auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token == SERVICE_KEY

@app.route("/log", methods=["POST"])
def write_log():
    # Capture the incoming header
    auth_header = request.headers.get("Authorization", "")
    print(f"[DEBUG] Received Authorization header: '{auth_header}'", file=sys.stderr)

    # Validate API key
    if not auth_header.startswith("Bearer "):
        print("[DEBUG] Missing or malformed Authorization header", file=sys.stderr)
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    if token != SERVICE_KEY:
        print(f"[DEBUG] Token mismatch! Expected '{SERVICE_KEY}' but got '{token}'", file=sys.stderr)
        return jsonify({"error": "Invalid key"}), 403

    # Extract log payload
    data = request.get_json(force=True) or {}
    print(f"[DEBUG] Received payload: {data}", file=sys.stderr)

    service = data.get("service")
    level = data.get("level", "INFO")
    message = data.get("message")
    context = data.get("context")

    if not service or not message:
        print("[DEBUG] Missing required fields: service or message", file=sys.stderr)
        return jsonify({"error": "Missing required fields"}), 400

    # Insert into database
    insert_log(service, level, message, json.dumps(context) if context else None)
    print("[DEBUG] Log successfully inserted into database", file=sys.stderr)

    return jsonify({"status": "logged"}), 201


@app.route("/logs", methods=["GET"])
def get_logs():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    session = SessionLocal()
    logs = session.query(Log).order_by(Log.timestamp.desc()).limit(10).all()
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
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    session = SessionLocal()
    logs = session.query(Log).order_by(Log.timestamp.desc()).all()
    session.close()

    # Format logs into plain text or CSV-like lines
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
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    session = SessionLocal()
    session.query(Log).delete()
    session.commit()
    session.close()

    return jsonify({"status": "purged"})

if __name__ == "__main__":
    app.run(port=5001)
