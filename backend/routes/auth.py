# auth.py
from flask import Blueprint, request, jsonify
from models import db, User
from flask_bcrypt import Bcrypt
from flask import Blueprint, request, jsonify, session
from extensions import db, bcrypt
from datetime import datetime, timedelta
import random
from flask_mail import Message
from extensions import mail
bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)

# ----------------- REGISTER ROUTE -----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Extract fields
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    email = data.get("email")

    # Basic validations
    if not username or not password or not full_name or not email:
        return jsonify({"error": "Missing required fields"}), 400

    # Check for existing username/email
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create user
    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        contact_number=data.get("contact_number"),
        address=data.get("address"),
        guardian_name=data.get("guardian_name"),
        guardian_number=data.get("guardian_number"),
        initials=data.get("initials"),
        image_filename=data.get("image_filename"),
        role=data.get("role", "user")  # default = user
    )
    new_user.set_password(password)

    # Save to DB
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    # Save user info in session (optional)
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }), 200


# ----------------- Logout -----------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route("/user", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }), 200
# ----------------- Forgot Password -----------------
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Generate 6-digit reset code
    code = str(random.randint(100000, 999999))
    user.reset_code = code
    user.reset_code_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    # Send email with reset code
    try:
        msg = Message(
            subject="Password Reset Code",
            sender="sithijamudalige15@gmail.com",  # Replace with your email
            recipients=[user.email],
            body=f"Your reset code is: {code}. It expires in 10 minutes."
        )
        mail.send(msg)
        return jsonify({"message": "Reset code sent to email"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error sending reset code"}), 500


# ----------------- Reset Password -----------------
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    if not email or not code or not new_password:
        return jsonify({"message": "Email, code, and new password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.reset_code != code:
        return jsonify({"message": "Invalid reset code"}), 400

    if datetime.utcnow() > user.reset_code_expiry:
        return jsonify({"message": "Reset code expired"}), 400

    user.set_password(new_password)  # uses bcrypt
    user.reset_code = None
    user.reset_code_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200