import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db, bcrypt, mail, migrate
from routes.auth import auth_bp
from routes.super_admin import super_admin_bp
from routes.teacher import teacher_bp
from routes.courses import course_bp

UPLOAD_FOLDER = "uploads/teachers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "users")



def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(super_admin_bp, url_prefix="/api/super-admin")
    app.register_blueprint(teacher_bp, url_prefix="/api/teachers")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(course_bp, url_prefix="/api/courses")
    # Upload folders
    USERS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "users")
    TEACHERS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "teachers")
    os.makedirs(USERS_UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEACHERS_UPLOAD_FOLDER, exist_ok=True)

    # Routes to serve uploaded images
    @app.route("/uploads/users/<filename>")
    def uploaded_user_file(filename):
        return send_from_directory(USERS_UPLOAD_FOLDER, filename)

    @app.route("/uploads/teachers/<filename>")
    def uploaded_teacher_file(filename):
        return send_from_directory(TEACHERS_UPLOAD_FOLDER, filename)

    return app




if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
