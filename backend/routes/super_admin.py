from flask import Blueprint, request, jsonify, session

super_admin_bp = Blueprint("super_admin_bp", __name__)

SUPER_ADMIN_USERNAME = "reda"
SUPER_ADMIN_PASSWORD = "20180807"

@super_admin_bp.route("/login", methods=["POST"])
def super_admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
        session["super_admin"] = True
        return jsonify({"message": "Super Admin login successful!"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@super_admin_bp.route("/logout", methods=["POST"])
def super_admin_logout():
    session.pop("super_admin", None)
    return jsonify({"message": "Super Admin logged out successfully!"}), 200
