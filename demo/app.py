"""
Safe API design demo (local use only, fictional data).

Demonstrates, in one small Flask app:
  - Token authentication (signed, expiring tokens; salted password hashes)
  - Object-level authorisation (users can only touch their own notes)
  - Input validation (content type, size, schema, unknown fields rejected)
  - Output shaping (explicit response fields only)
  - Rate limiting (sliding window, stricter on login)
  - Safe error handling (generic messages + request ID, no stack traces)
  - Transport-related headers (HSTS etc.; TLS itself is done by a proxy)
  - Secrets from environment (nothing hardcoded)
  - Safe logging (no passwords, tokens or note contents)
  - Versioning and deprecation signalling (/api/v0 -> /api/v1)

All users and notes below are FICTIONAL. Do not expose this to the internet.
Run:  python app.py        (listens on 127.0.0.1:5000 only)
"""
import logging
import os
import secrets
import time
import uuid
from collections import defaultdict, deque
from functools import wraps

from flask import Flask, g, jsonify, request, send_from_directory
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

# --------------------------------------------------------------------------
# Configuration (secrets come from the environment, never from source code)
# --------------------------------------------------------------------------
SECRET_KEY = os.environ.get("DEMO_SECRET_KEY") or secrets.token_urlsafe(32)
TOKEN_TTL_SECONDS = 15 * 60
MAX_BODY_BYTES = 10 * 1024
RATE_LIMIT_DEFAULT = (60, 60)  # 60 requests per 60 seconds
RATE_LIMIT_LOGIN = (5, 60)     # 5 login attempts per 60 seconds
DEPRECATION_TS = 1767225600    # 2026-01-01T00:00:00Z (fictional)
SUNSET_HTTP_DATE = "Wed, 31 Mar 2027 23:59:59 GMT"  # fictional
START_TIME = time.monotonic()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="demo-auth-token")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-api")

# --------------------------------------------------------------------------
# Fictional data (in memory)
# --------------------------------------------------------------------------
USERS = {
    "alice": {"id": "u-1001", "pw": generate_password_hash("demo-password-alice")},
    "bob": {"id": "u-1002", "pw": generate_password_hash("demo-password-bob")},
}
USER_BY_ID = {user["id"]: username for username, user in USERS.items()}
# Dummy hash used so unknown usernames cost the same time as known ones.
_DUMMY_HASH = generate_password_hash("not-a-real-password")

NOTES = {}  # note_id -> {"id", "owner_id", "title", "body", "created_at"}


def _seed():
    for owner, title in (("u-1001", "Alice's first note"), ("u-1002", "Bob's first note")):
        nid = str(uuid.uuid4())
        NOTES[nid] = {
            "id": nid, "owner_id": owner, "title": title,
            "body": "Fictional demo content.", "created_at": int(time.time()),
            "internal_flag": "never-returned-to-clients",
        }


_seed()

# --------------------------------------------------------------------------
# Rate limiting (in-memory sliding window; use Redis or a gateway in production)
# --------------------------------------------------------------------------
_hits = defaultdict(deque)


def rate_limited(key, limit):
    max_req, window = limit
    now = time.monotonic()
    q = _hits[key]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= max_req:
        retry_after = max(1, int(window - (now - q[0])))
        return retry_after, 0, retry_after
    q.append(now)
    remaining = max(0, max_req - len(q))
    reset_after = max(1, int(window - (now - q[0]))) if q else 0
    return None, remaining, reset_after


def reset_rate_limits():
    """Used by tests only."""
    _hits.clear()


# --------------------------------------------------------------------------
# Error helper: consistent shape, generic text, request ID for support
# --------------------------------------------------------------------------
def error(status, code, message, headers=None):
    body = {"error": {"code": code, "message": message, "request_id": g.get("request_id")}}
    resp = jsonify(body)
    resp.status_code = status
    for k, v in (headers or {}).items():
        resp.headers[k] = v
    return resp


def get_client_ip():
    return request.remote_addr or "unknown"


# --------------------------------------------------------------------------
# Request lifecycle hooks
# --------------------------------------------------------------------------
@app.before_request
def start_request():
    g.request_id = uuid.uuid4().hex[:12]
    g.user_id = None
    g.start = time.monotonic()
    g.rate_limit_limit = None
    g.rate_limit_remaining = None
    g.rate_limit_reset = None

    # Rate limit by IP before doing any work.
    limit = RATE_LIMIT_LOGIN if request.path.endswith("/login") else RATE_LIMIT_DEFAULT
    rate_key = f"{get_client_ip()}:{request.path.endswith('/login')}"
    retry, remaining, reset_after = rate_limited(rate_key, limit)
    g.rate_limit_limit = str(limit[0])
    g.rate_limit_remaining = str(remaining)
    g.rate_limit_reset = str(reset_after)
    if retry is not None:
        return error(429, "rate_limited", "Too many requests. Try again later.",
                     {"Retry-After": str(retry)})

    # Reject non-JSON bodies on write methods early.
    if request.method in ("POST", "PUT", "PATCH") and request.content_length:
        if request.mimetype != "application/json":
            return error(415, "unsupported_media_type", "Content-Type must be application/json.")


@app.after_request
def finish_request(resp):
    # Security headers (HSTS only takes effect when served over HTTPS).
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'"
    )
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    resp.headers["X-Request-ID"] = g.get("request_id", "-")
    if g.get("rate_limit_limit") is not None:
        resp.headers["X-RateLimit-Limit"] = g.get("rate_limit_limit")
        resp.headers["X-RateLimit-Remaining"] = g.get("rate_limit_remaining")
        resp.headers["X-RateLimit-Reset"] = g.get("rate_limit_reset")
    resp.headers.pop("Server", None)

    # Deprecated version signalling (RFC 9745 Deprecation, RFC 8594 Sunset).
    if request.path.startswith("/api/v0/"):
        resp.headers["Deprecation"] = f"@{DEPRECATION_TS}"
        resp.headers["Sunset"] = SUNSET_HTTP_DATE
        resp.headers["Link"] = '</api/v1/notes>; rel="successor-version"'

    # Safe log line: no tokens, passwords, bodies or query strings.
    log.info("req=%s method=%s path=%s status=%s user=%s ms=%d",
             g.get("request_id"), request.method, request.path, resp.status_code,
             g.get("user_id") or "-", int((time.monotonic() - g.get("start", time.monotonic())) * 1000))
    return resp


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    # Covers 404, 405, 413 etc. with our own generic messages.
    messages = {
        404: ("not_found", "Resource not found."),
        405: ("method_not_allowed", "Method not allowed."),
        413: ("payload_too_large", "Request body too large."),
    }
    code, msg = messages.get(e.code, ("http_error", "Request could not be processed."))
    return error(e.code, code, msg)


@app.errorhandler(Exception)
def handle_unexpected(e):
    # Full detail goes to the server log only, never to the client.
    log.exception("req=%s unhandled error", g.get("request_id"))
    return error(500, "internal_error", "Something went wrong.")


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return error(401, "unauthenticated", "Authentication required.",
                         {"WWW-Authenticate": "Bearer"})
        try:
            data = serializer.loads(token, max_age=TOKEN_TTL_SECONDS)
        except (BadSignature, SignatureExpired):
            return error(401, "unauthenticated", "Invalid or expired token.",
                         {"WWW-Authenticate": "Bearer"})
        if not isinstance(data, dict) or "uid" not in data:
            return error(401, "unauthenticated", "Invalid or expired token.",
                         {"WWW-Authenticate": "Bearer"})
        g.user_id = data.get("uid")
        return fn(*args, **kwargs)
    return wrapper


def get_json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data


@app.get("/")
@app.get("/ui")
def serve_ui():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "index.html")


@app.post("/api/v1/login")
def login():
    data = get_json_body()
    if data is None or set(data) != {"username", "password"} \
            or not all(isinstance(data[k], str) for k in data):
        return error(400, "invalid_request", "Provide username and password as strings.")
    user = USERS.get(data["username"])
    # Always run a hash check so timing does not reveal whether a user exists.
    ok = check_password_hash(user["pw"] if user else _DUMMY_HASH, data["password"])
    if not user or not ok:
        return error(401, "invalid_credentials", "Invalid username or password.")
    token = serializer.dumps({"uid": user["id"]})
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": TOKEN_TTL_SECONDS})


# --------------------------------------------------------------------------
# Input validation and output shaping
# --------------------------------------------------------------------------
ALLOWED_CREATE_FIELDS = {"title", "body"}


def validate_note_payload(data):
    """Return (clean_dict, error_message). Allow-list, types, lengths, no unknown fields."""
    if data is None:
        return None, "Body must be a JSON object."
    unknown = set(data) - ALLOWED_CREATE_FIELDS
    if unknown:
        return None, "Unknown field(s) not allowed."
    title, body = data.get("title"), data.get("body", "")
    if not isinstance(title, str) or not (1 <= len(title.strip()) <= 100):
        return None, "title must be a string of 1-100 characters."
    if not isinstance(body, str) or len(body) > 1000:
        return None, "body must be a string of at most 1000 characters."
    return {"title": title.strip(), "body": body}, None


def public_note(n):
    """Explicit allow-list of fields returned to the client."""
    return {"id": n["id"], "title": n["title"], "body": n["body"], "created_at": n["created_at"]}


def parse_uuid(value):
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Resource endpoints (v1)
# --------------------------------------------------------------------------
@app.post("/api/v1/notes")
@require_auth
def create_note():
    clean, err = validate_note_payload(get_json_body())
    if err:
        return error(400, "validation_error", err)
    nid = str(uuid.uuid4())
    NOTES[nid] = {"id": nid, "owner_id": g.user_id, "created_at": int(time.time()),
                  "internal_flag": "set-by-server", **clean}  # owner comes from the token, never the body
    resp = jsonify(public_note(NOTES[nid]))
    resp.status_code = 201
    resp.headers["Location"] = f"/api/v1/notes/{nid}"
    return resp


@app.get("/api/v1/health")
def healthcheck():
    return jsonify({
        "status": "ok",
        "service": "demo-api",
        "version": "v1",
        "uptime_seconds": round(time.monotonic() - START_TIME, 2),
    })


@app.get("/api/v1/me")
@require_auth
def current_user():
    username = USER_BY_ID.get(g.user_id, "unknown")
    return jsonify({"id": g.user_id, "username": username})


@app.get("/api/v1/notes")
@require_auth
def list_notes():
    # Query is scoped to the caller; paginated with a hard cap.
    try:
        raw_limit = int(request.args.get("limit", 20))
        raw_offset = int(request.args.get("offset", 0))
    except ValueError:
        return error(400, "validation_error", "limit and offset must be integers.")
    if raw_limit <= 0 or raw_offset < 0:
        return error(400, "validation_error", "limit must be greater than 0 and offset must be zero or greater.")

    limit = min(raw_limit, 50)
    offset = raw_offset
    mine = [public_note(n) for n in NOTES.values() if n["owner_id"] == g.user_id]
    total = len(mine)
    page = mine[offset:offset + limit]
    return jsonify({"items": page, "limit": limit, "offset": offset, "total": total})


@app.get("/api/v1/notes/<note_id>")
@require_auth
def get_note(note_id):
    nid = parse_uuid(note_id)
    note = NOTES.get(nid) if nid else None
    # Object-level authorisation: not yours -> same 404 as "does not exist".
    if note is None or note["owner_id"] != g.user_id:
        return error(404, "not_found", "Resource not found.")
    return jsonify(public_note(note))


@app.put("/api/v1/notes/<note_id>")
@require_auth
def update_note(note_id):
    nid = parse_uuid(note_id)
    note = NOTES.get(nid) if nid else None
    if note is None or note["owner_id"] != g.user_id:
        return error(404, "not_found", "Resource not found.")

    clean, err = validate_note_payload(get_json_body())
    if err:
        return error(400, "validation_error", err)

    note.update(clean)
    return jsonify(public_note(note))


@app.delete("/api/v1/notes/<note_id>")
@require_auth
def delete_note(note_id):
    nid = parse_uuid(note_id)
    note = NOTES.get(nid) if nid else None
    if note is None or note["owner_id"] != g.user_id:
        return error(404, "not_found", "Resource not found.")
    del NOTES[nid]
    return "", 204


# --------------------------------------------------------------------------
# Deprecated version (kept briefly to show Deprecation/Sunset headers)
# --------------------------------------------------------------------------
@app.get("/api/v0/notes")
@require_auth
def list_notes_v0():
    mine = [public_note(n) for n in NOTES.values() if n["owner_id"] == g.user_id]
    return jsonify({"items": mine})


if __name__ == "__main__":
    # Bind to localhost only. Never run the Flask dev server in production.
    app.run(host="127.0.0.1", port=5000, debug=False)
