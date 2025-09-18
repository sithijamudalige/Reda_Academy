# models.py
from extensions import db, bcrypt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------- User Model -----------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(50), default="user")
    full_name = db.Column(db.String(150), nullable=False)
    initials = db.Column(db.String(10), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    guardian_name = db.Column(db.String(150), nullable=True)
    guardian_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expiry = db.Column(db.DateTime, nullable=True)
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)


# ----------------- Login History Model -----------------
class LoginHistory(db.Model):
    __tablename__ = "login_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    success = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref="login_history")


# ----------------- Teacher Model -----------------
class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    lecturer_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    telephone = db.Column(db.String(15))
    qualification = db.Column(db.String(200))
    rate_per_hour = db.Column(db.Numeric(10, 2))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    module_name = db.Column(db.String(100))
    no_of_hours_allocated = db.Column(db.Integer)
    profile_picture = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
