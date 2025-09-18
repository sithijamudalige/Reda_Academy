# routes/teacher.py
from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
from models import Teacher, db

teacher_bp = Blueprint("teacher_bp", __name__)

# Upload folder
UPLOAD_FOLDER = "uploads/teachers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Serve uploaded files
@teacher_bp.route("/uploads/teachers/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# GET all teachers
@teacher_bp.route("/", methods=["GET"])
def get_teachers():
    if not session.get("super_admin"):
        return jsonify({"message": "Unauthorized"}), 401

    teachers = Teacher.query.all()
    result = [
        {
            "id": t.id,
            "lecturer_name": t.lecturer_name,
            "address": t.address,
            "telephone": t.telephone,
            "qualification": t.qualification,
            "rate_per_hour": str(t.rate_per_hour),
            "username": t.username,
            "module_name": t.module_name,
            "no_of_hours_allocated": t.no_of_hours_allocated,
            "profile_picture": f"http://localhost:5000/{t.profile_picture}" if t.profile_picture else None,
        }
        for t in teachers
    ]
    return jsonify(result)


# GET single teacher
@teacher_bp.route("/<int:id>", methods=["GET"])
def get_teacher(id):
    if not session.get("super_admin"):
        return jsonify({"message": "Unauthorized"}), 401

    teacher = Teacher.query.get_or_404(id)
    result = {
        "id": teacher.id,
        "lecturer_name": teacher.lecturer_name,
        "address": teacher.address,
        "telephone": teacher.telephone,
        "qualification": teacher.qualification,
        "rate_per_hour": str(teacher.rate_per_hour),
        "username": teacher.username,
        "module_name": teacher.module_name,
        "no_of_hours_allocated": teacher.no_of_hours_allocated,
        "profile_picture": f"http://localhost:5000/{teacher.profile_picture}" if teacher.profile_picture else None,
    }
    return jsonify(result)


# ADD teacher
@teacher_bp.route("/add", methods=["POST"])
def add_teacher():
    if not session.get("super_admin"):
        return jsonify({"message": "Unauthorized"}), 401

    data = request.form
    username = data.get("username")
    password = data.get("password")
    lecturer_name = data.get("lecturer_name")

    if not username or not password or not lecturer_name:
        return jsonify({"message": "Username, password, and lecturer name are required"}), 400

    # Check for unique username
    if Teacher.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    teacher = Teacher(
        lecturer_name=lecturer_name,
        username=username,
        module_name=data.get("module_name"),
        rate_per_hour=data.get("rate_per_hour") or 0,
        no_of_hours_allocated=data.get("no_of_hours_allocated") or 0,
        address=data.get("address"),
        telephone=data.get("telephone"),
        qualification=data.get("qualification"),
    )
    teacher.password_hash = generate_password_hash(password)

    # Handle profile picture
    file = request.files.get("profile_pic")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        teacher.profile_picture = f"{UPLOAD_FOLDER}/{filename}"

    db.session.add(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher added successfully!"})


# UPDATE teacher
@teacher_bp.route("/<int:id>", methods=["PUT"])
def update_teacher(id):
    if not session.get("super_admin"):
        return jsonify({"message": "Unauthorized"}), 401

    teacher = Teacher.query.get_or_404(id)
    form = request.form

    # List of updatable fields
    fields = [
        "lecturer_name",
        "address",
        "telephone",
        "qualification",
        "rate_per_hour",
        "username",
        "module_name",
        "no_of_hours_allocated",
        "password",
    ]

    for field in fields:
        if field in form and form[field]:
            if field == "password":
                teacher.password_hash = generate_password_hash(form[field])
            else:
                setattr(teacher, field, form[field])

    # Update profile picture
    if "profile_pic" in request.files:
        pic = request.files["profile_pic"]
        if pic and allowed_file(pic.filename):
            filename = secure_filename(pic.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            pic.save(file_path)
            teacher.profile_picture = f"{UPLOAD_FOLDER}/{filename}"

    db.session.commit()
    return jsonify({"message": "Teacher updated successfully"})


# DELETE teacher
@teacher_bp.route("/<int:id>", methods=["DELETE"])
def delete_teacher(id):
    if not session.get("super_admin"):
        return jsonify({"message": "Unauthorized"}), 401

    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted successfully"})
