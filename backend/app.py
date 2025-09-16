from flask import Flask, request, jsonify, send_from_directory, session, Blueprint
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
import os
from datetime import datetime

from config import Config
from models import db, User, Techer, LoginHistory, bcrypt

# ----------------- Initialize Flask App -----------------
app = Flask(__name__)

# ----------------- Configuration -----------------
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1230@localhost/online_learning_platform_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True
)

# ----------------- File Upload Configuration -----------------
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Initialize Extensions -----------------
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# ----------------- Super Admin Credentials -----------------
SUPER_ADMIN_USERNAME = "reda"
SUPER_ADMIN_PASSWORD = "20180807"

# ----------------- Teacher Blueprint -----------------
teacher_bp = Blueprint("teacher_bp", __name__)

# ----------------- Routes -----------------
@app.route("/api/test")
def test():
    return {"msg": "CORS is working!"}

# -------- Signup --------
@app.route("/api/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    full_name = request.form.get("full_name")
    initials = request.form.get("initials")
    contact_number = request.form.get("contact_number")
    address = request.form.get("address")
    guardian_name = request.form.get("guardian_name")
    guardian_number = request.form.get("guardian_number")
    image = request.files.get("image")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    image_filename = None
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    user = User(
        username=username,
        email=email,
        role="user",
        full_name=full_name,
        initials=initials,
        contact_number=contact_number,
        address=address,
        guardian_name=guardian_name,
        guardian_number=guardian_number,
        image_filename=image_filename
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Error saving user. Username or email might already exist."}), 400

    return jsonify({"message": "User registered successfully"}), 201

# -------- Login --------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        session['user_id'] = user.id
        return jsonify({"message": "Logged in successfully"})

    return jsonify({"message": "Invalid credentials"}), 401

# -------- Serve Uploaded Images --------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/user", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "initials": user.initials,
        "contact_number": user.contact_number,
        "address": user.address,
        "guardian_name": user.guardian_name,
        "guardian_number": user.guardian_number,
        "image_url": f"http://localhost:5000/uploads/{user.image_filename}" if user.image_filename else None
    })


# -------- Super Admin Login & Logout --------
@app.route("/api/super-admin/login", methods=["POST"])
def super_admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
        session['super_admin_logged_in'] = True
        return jsonify({"message": "Super admin logged in successfully"}), 200
    return jsonify({"message": "Invalid super admin credentials"}), 401

@app.route("/api/super-admin/logout", methods=["POST"])
def super_admin_logout():
    session.pop('super_admin_logged_in', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/api/super-admin/dashboard", methods=["GET"])
def super_admin_dashboard():
    if not session.get('super_admin_logged_in'):
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify({"message": "Welcome to Super Admin Dashboard!"}), 200

# ----------------- Teacher Blueprint Routes -----------------

# Add Teacher
@teacher_bp.route("/add", methods=["POST"])
def add_teacher():
    if not session.get("super_admin_logged_in"):
        return jsonify({"message": "Unauthorized"}), 401

    try:
        lecturer_name = request.form.get("lecturer_name")
        address = request.form.get("address")
        telephone = request.form.get("telephone")
        qualification = request.form.get("qualification")
        rate_per_hour = request.form.get("rate_per_hour")
        username = request.form.get("username")
        password = request.form.get("password")
        module_name = request.form.get("module_name")
        no_of_hours_allocated = request.form.get("no_of_hours_allocated")

        if rate_per_hour:
            rate_per_hour = float(rate_per_hour)
        if no_of_hours_allocated:
            no_of_hours_allocated = int(no_of_hours_allocated)

        profile_pic = None
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                profile_pic = f"/uploads/{filename}"

        teacher = Techer(
            lecturer_name=lecturer_name,
            address=address,
            telephone=telephone,
            qualification=qualification,
            rate_per_hour=rate_per_hour,
            username=username,
            module_name=module_name,
            no_of_hours_allocated=no_of_hours_allocated,
            profile_picture=profile_pic
        )

        if password:
            teacher.set_password(password)

        db.session.add(teacher)
        db.session.commit()

        return jsonify({"message": "Teacher added successfully"}), 201

    except ValueError:
        return jsonify({"message": "Invalid number format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding teacher", "error": str(e)}), 500

# Get all teachers
@teacher_bp.route("/", methods=["GET"])
def get_teachers():
    if not session.get("super_admin_logged_in"):
        return jsonify({"message": "Unauthorized"}), 401

    teachers = Techer.query.all()
    result = []
    for t in teachers:
        result.append({
            "id": t.id,
            "lecturer_name": t.lecturer_name,
            "address": t.address,
            "telephone": t.telephone,
            "qualification": t.qualification,
            "rate_per_hour": str(t.rate_per_hour),
            "username": t.username,
            "module_name": t.module_name,
            "no_of_hours_allocated": t.no_of_hours_allocated,
            "profile_picture": f"http://localhost:5000{t.profile_picture}" if t.profile_picture else None
        })
    return jsonify(result)

# Get single teacher
@teacher_bp.route("/<int:id>", methods=["GET"])
def get_teacher(id):
    if not session.get("super_admin_logged_in"):
        return jsonify({"message": "Unauthorized"}), 401

    t = Techer.query.get_or_404(id)
    return jsonify({
        "id": t.id,
        "lecturer_name": t.lecturer_name,
        "address": t.address,
        "telephone": t.telephone,
        "qualification": t.qualification,
        "rate_per_hour": str(t.rate_per_hour),
        "username": t.username,
        "module_name": t.module_name,
        "no_of_hours_allocated": t.no_of_hours_allocated,
        "profile_picture": f"http://localhost:5000{t.profile_picture}" if t.profile_picture else None
    })

# Update teacher
@teacher_bp.route("/<int:id>", methods=["PUT"])
def update_teacher(id):
    if not session.get("super_admin_logged_in"):
        return jsonify({"message": "Unauthorized"}), 401

    teacher = Techer.query.get_or_404(id)

    try:
        # Use form data instead of JSON
        lecturer_name = request.form.get("lecturer_name", teacher.lecturer_name)
        address = request.form.get("address", teacher.address)
        telephone = request.form.get("telephone", teacher.telephone)
        qualification = request.form.get("qualification", teacher.qualification)
        rate_per_hour = request.form.get("rate_per_hour", teacher.rate_per_hour)
        module_name = request.form.get("module_name", teacher.module_name)
        no_of_hours_allocated = request.form.get("no_of_hours_allocated", teacher.no_of_hours_allocated)
        password = request.form.get("password")

        # Convert numeric fields
        try:
            rate_per_hour = float(rate_per_hour)
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid rate_per_hour"}), 400
        try:
            no_of_hours_allocated = int(no_of_hours_allocated)
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid no_of_hours_allocated"}), 400

        # Update fields
        teacher.lecturer_name = lecturer_name
        teacher.address = address
        teacher.telephone = telephone
        teacher.qualification = qualification
        teacher.rate_per_hour = rate_per_hour
        teacher.module_name = module_name
        teacher.no_of_hours_allocated = no_of_hours_allocated
         # Username iseditable
        teacher.username = teacher.username
        teacher.profile_picture = teacher.profile_picture  # Keep existing picture unless updated
        if password:
            teacher.set_password(password)
            


        # Handle profile picture if uploaded
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                teacher.profile_picture = f"/uploads/{filename}"

        db.session.commit()
        return jsonify({"message": "Teacher updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating teacher", "error": str(e)}), 500


# Delete teacher
@teacher_bp.route("/<int:id>", methods=["DELETE"])
def delete_teacher(id):
    if not session.get("super_admin_logged_in"):
        return jsonify({"message": "Unauthorized"}), 401

    teacher = Techer.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted successfully"})

# ----------------- Register Blueprint -----------------
app.register_blueprint(teacher_bp, url_prefix="/api/teachers")

# ----------------- Run Server -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
