from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from extensions import db
from models import Course
import os
import uuid

course_bp = Blueprint("courses", __name__)

# ----------------- File Upload Config -----------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "courses")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ----------------- Add Course -----------------
@course_bp.route("/add", methods=["POST"])
def add_course():
    try:
        data = request.form
        file = request.files.get("cover_photo")
        filename = None

        # Save cover photo with UUID prefix
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        course = Course(
            course_name=data.get("course_name"),
            course_duration=data.get("course_duration"),
            cover_photo=filename,
            course_description=data.get("course_description"),
            course_syllabus=data.get("course_syllabus"),
            teacher_name=data.get("teacher_name"),
            teacher_qualification=data.get("teacher_qualification"),
            duration=data.get("duration"),   # ✅ keep only if it's a separate field
            payment=data.get("payment"),
            full_price=safe_float(data.get("full_price")),
            admission_fees=safe_float(data.get("admission_fees")),
        )

        db.session.add(course)
        db.session.commit()
        return jsonify({"message": "Course added successfully!"}), 201
    except Exception as e:
        print("Add Course Error:", e)
        return jsonify({"error": "Failed to add course"}), 500


# ----------------- Get All Courses -----------------
@course_bp.route("/", methods=["GET"])
def get_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses]), 200


# ----------------- Get Single Course -----------------
@course_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course.to_dict()), 200


# ----------------- Update Course -----------------
@course_bp.route("/update/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.form
    file = request.files.get("cover_photo")

    if file and allowed_file(file.filename):
        # Delete old file if exists
        if course.cover_photo:
            old_path = os.path.join(UPLOAD_FOLDER, course.cover_photo)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Save new file with UUID prefix
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        course.cover_photo = filename

    # Update fields safely
    course.course_name = data.get("course_name", course.course_name)
    course.course_duration = data.get("course_duration", course.course_duration)
    course.course_description = data.get("course_description", course.course_description)
    course.course_syllabus = data.get("course_syllabus", course.course_syllabus)
    course.teacher_name = data.get("teacher_name", course.teacher_name)
    course.teacher_qualification = data.get("teacher_qualification", course.teacher_qualification)
    course.duration = data.get("duration", course.duration)
    course.payment = data.get("payment", course.payment)
    course.full_price = safe_float(data.get("full_price"), course.full_price)
    course.admission_fees = safe_float(data.get("admission_fees"), course.admission_fees)

    db.session.commit()
    return jsonify({"message": "Course updated successfully!"}), 200


# ----------------- Delete Course -----------------
@course_bp.route("/delete/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Delete cover photo file if exists
    if course.cover_photo:
        photo_path = os.path.join(UPLOAD_FOLDER, course.cover_photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully!"}), 200


# ----------------- Serve Course Images -----------------
@course_bp.route("/cover/<filename>", methods=["GET"])
def get_cover(filename):
    """Serve uploaded course cover images safely"""
    return send_from_directory(UPLOAD_FOLDER, filename)
