from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from extensions import db
from models import Course
import os

course_bp = Blueprint("courses", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "courses")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Add Course -----------------
@course_bp.route("/add", methods=["POST"])
def add_course():
    try:
        data = request.form
        file = request.files.get("cover_photo")
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        course = Course(
            course_name=data.get("course_name"),
            course_duration=data.get("course_duration"),
            cover_photo=filename,
            course_description=data.get("course_description"),
            course_syllabus=data.get("course_syllabus"),
            teacher_name=data.get("teacher_name"),
            teacher_qualification=data.get("teacher_qualification"),
            duration=data.get("duration"),
            payment=data.get("payment"),
            full_price=float(data.get("full_price", 0)),
            admission_fees=float(data.get("admission_fees", 0)),
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
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        course.cover_photo = filename

    course.course_name = data.get("course_name", course.course_name)
    course.course_duration = data.get("course_duration", course.course_duration)
    course.course_description = data.get("course_description", course.course_description)
    course.course_syllabus = data.get("course_syllabus", course.course_syllabus)
    course.teacher_name = data.get("teacher_name", course.teacher_name)
    course.teacher_qualification = data.get("teacher_qualification", course.teacher_qualification)
    course.duration = data.get("duration", course.duration)
    course.payment = data.get("payment", course.payment)
    course.full_price = float(data.get("full_price", course.full_price))
    course.admission_fees = float(data.get("admission_fees", course.admission_fees))

    db.session.commit()
    return jsonify({"message": "Course updated successfully!"}), 200

# ----------------- Delete Course -----------------
@course_bp.route("/delete/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully!"}), 200
