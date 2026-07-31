"""
NUM-OSINT Web Server Backend
Flask Application with Upstream JSON Branding Transformation & Sanitization
"""

import os
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder="web")

# Rate Throttling
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)

# Configuration loaded strictly from .env
API_URL = os.getenv("API_URL")

# Enterprise Security Headers & CORS
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self';"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# JSON Sanitization Helper: Strips third-party reseller tags and injects official user branding
def sanitize_payload(json_data):
    if not isinstance(json_data, dict):
        return json_data

    clean_data = {}
    for key, val in json_data.items():
        k_str = str(key).strip()
        k_upper = k_str.upper()

        # Filter out BUY_API, SUPPORT, and reseller branding fields
        if any(unwanted in k_upper for unwanted in ["BUY_API", "SUPPORT", "EXPLOITSCOLLECTIVE", "SELLER", "BUY_"]):
            continue

        clean_data[k_str] = val

    # Inject User Branding into JSON payload
    clean_data["DEVELOPER"] = "Lucky"
    clean_data["SYSTEM"]    = "NUM-OSINT v2.0"

    return clean_data

# Serve Frontend Static Files
@app.route("/")
def serve_index():
    return send_from_directory("web", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join("web", path)):
        return send_from_directory("web", path)
    return send_from_directory("web", "index.html")

# Live API Lookup Endpoint
@app.route("/api/lookup", methods=["GET"])
@limiter.limit("40 per minute")
def api_lookup():
    # Input Sanitization: Strip whitespace & non-digit characters
    raw_input = request.args.get("number", "")
    sanitized_number = re.sub(r"\D", "", str(raw_input)).strip()

    # Input Validation: Strict 10-digit Indian Mobile Pattern (Starts with 6, 7, 8, or 9)
    if not re.match(r"^[6-9]\d{9}$", sanitized_number):
        return jsonify({
            "success": False,
            "error": "INVALID_INPUT",
            "message": "Please provide a valid 10-digit Indian mobile number."
        }), 400

    # Build Upstream Request URL
    if API_URL.endswith("="):
        target_url = API_URL + sanitized_number
    elif "num=" in API_URL:
        target_url = re.sub(r'num=[^&]*', f'num={sanitized_number}', API_URL)
    else:
        target_url = API_URL + sanitized_number

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NUM-OSINT-Engine/2.0",
        "Accept": "application/json"
    }

    try:
        upstream_resp = requests.get(target_url, headers=headers, timeout=15)
        
        if upstream_resp.status_code == 200:
            try:
                raw_json = upstream_resp.json()

                # Clean & inject branding into JSON
                cleaned_json = sanitize_payload(raw_json)
                results_list = cleaned_json.get("result", [])

                return jsonify({
                    "success": True,
                    "query_number": sanitized_number,
                    "count": len(results_list) if isinstance(results_list, list) else (1 if results_list else 0),
                    "data": cleaned_json,
                    "source": "NUM_OSINT_ENGINE"
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": "PARSING_ERROR",
                    "message": "Unable to parse telemetry response from upstream API."
                }), 502
        else:
            return jsonify({
                "success": False,
                "error": "UPSTREAM_ERROR",
                "message": "Upstream API returned an invalid response."
            }), 502

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "TIMEOUT",
            "message": "Upstream request timed out. Please try again."
        }), 504
    except Exception as err:
        return jsonify({
            "success": False,
            "error": "CONNECTION_ERROR",
            "message": "Connection failure connecting to intelligence API."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
