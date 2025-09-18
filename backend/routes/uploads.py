from flask import Blueprint, send_from_directory, current_app, abort
import os

uploads_bp = Blueprint("uploads_bp", __name__)

@uploads_bp.route("/<path:filename>")
def uploaded_file(filename):
    try:
        upload_folder = current_app.config.get("UPLOAD_FOLDER")

        if not upload_folder:
            abort(500, description="UPLOAD_FOLDER is not configured")

        # Prevent path traversal (e.g., ../../../etc/passwd)
        safe_path = os.path.join(upload_folder, os.path.normpath(filename))
        if not os.path.isfile(safe_path):
            abort(404, description="File not found")

        return send_from_directory(upload_folder, filename)

    except Exception as e:
        abort(500, description=str(e))
