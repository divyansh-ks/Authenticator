"""
TOTP Authenticator - Flask Backend
Based on RFC 6238 TOTP Algorithm
"""

import hmac
import hashlib
import struct
import time
import base64
import math
import json
import uuid
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ── TOTP Core (RFC 6238 / RFC 4226 HOTP) ──────────────────────────────────────

def _base32_decode(secret: str) -> bytes:
    """Decode a base32 secret, padding as needed."""
    secret = secret.upper().replace(" ", "")
    padding = (8 - len(secret) % 8) % 8
    secret += "=" * padding
    return base64.b32decode(secret)


def generate_totp(secret: str, period: int = 30, digits: int = 6) -> str:
    """Generate a TOTP code for the current time window."""
    try:
        key = _base32_decode(secret)
    except Exception:
        raise ValueError("Invalid base32 secret")

    counter = int(time.time()) // period

    # HMAC-SHA1 over the 8-byte big-endian counter
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = h[-1] & 0x0F
    code_int = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF
    code = code_int % (10 ** digits)
    return str(code).zfill(digits)


def time_remaining(period: int = 30) -> int:
    """Seconds remaining in the current TOTP window."""
    return period - (int(time.time()) % period)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Generate TOTP codes for one or more accounts.
    Request body: { "accounts": [{"id": "...", "secret": "..."}] }
    Response:     { "codes": {"<id>": "<6-digit-code>"}, "time_remaining": N }
    """
    data = request.get_json(force=True)
    accounts = data.get("accounts", [])

    codes = {}
    for acc in accounts:
        acc_id = acc.get("id")
        secret = acc.get("secret", "")
        try:
            codes[acc_id] = generate_totp(secret)
        except Exception:
            codes[acc_id] = "ERROR"

    return jsonify({"codes": codes, "time_remaining": time_remaining()})


@app.route("/api/validate_secret", methods=["POST"])
def api_validate_secret():
    """Quick validation that a secret can produce a TOTP code."""
    data = request.get_json(force=True)
    secret = data.get("secret", "")
    try:
        code = generate_totp(secret)
        return jsonify({"valid": True, "code": code})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
