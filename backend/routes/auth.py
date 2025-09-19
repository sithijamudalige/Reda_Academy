# auth.py
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from extensions import db, bcrypt, mail
from models import User
from flask_mail import Message
from datetime import datetime, timedelta
import random
import os

auth_bp = Blueprint("auth", __name__)

# ----------------- Upload Settings -----------------
UPLOAD_FOLDER = "uploads/users"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Register -----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact_number = request.form.get("contact_number")
        address = request.form.get("address")
        guardian_name = request.form.get("guardian_name")
        guardian_number = request.form.get("guardian_number")
        initials = request.form.get("initials")

        # Validate required fields
        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Handle profile image
        file = request.files.get("image")
        filename = None
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            else:
                return jsonify({"error": "Invalid image format"}), 400

        # Create user
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            contact_number=contact_number,
            address=address,
            guardian_name=guardian_name,
            guardian_number=guardian_number,
            initials=initials,
            image_filename=filename
        )

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 200

    except Exception as e:
        print("Register error:", e)
        return jsonify({"error": "Registration failed"}), 500

# ----------------- Login -----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("identifier")  # username or email
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"message": "Username/email and password are required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session.permanent = True

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "image_filename": user.image_filename
        }
    }), 200

# ----------------- Logout -----------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# ----------------- Get Current User -----------------
@auth_bp.route("/user", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    image_url = f"/uploads/users/{user.image_filename}" if user.image_filename else "/uploads/users/default.png"

    return jsonify({
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "contact_number": user.contact_number,
        "guardian_name": user.guardian_name,
        "guardian_number": user.guardian_number,
        "image_filename": user.image_filename,
        "image_url": image_url,
        "address": user.address,
        "initials": user.initials
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

    code = str(random.randint(100000, 999999))
    user.reset_code = code
    user.reset_code_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    try:
        msg = Message(
            subject="Password Reset Code",
            sender="sithijamudalige15@gmail.com",
            recipients=[user.email],
            body=f"Your reset code is: {code}. It expires in 10 minutes."
        )
        mail.send(msg)
        return jsonify({"message": "Reset code sent to email"}), 200
    except Exception as e:
        print("Forgot password error:", e)
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

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.reset_code = None
    user.reset_code_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200

# ----------------- Change Password -----------------
@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Not logged in"}), 401

    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"message": "Current and new passwords are required"}), 400

    user = User.query.get(user_id)
    if not user or not bcrypt.check_password_hash(user.password_hash, current_password):
        return jsonify({"message": "Invalid current password"}), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
