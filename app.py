from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    send_file,
    session,
    flash,
    url_for,
    get_flashed_messages,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadSignature
from functools import wraps
import pandas as pd
import os
import json
from datetime import datetime
from sqlalchemy import or_

from models import db, User, File, RecycleBin
from config import get_config

app = Flask(__name__)

# Load configuration based on environment
config_class = get_config()
app.config.from_object(config_class)

db.init_app(app)
serializer = URLSafeTimedSerializer(app.secret_key)


# Create upload folder with error handling
def ensure_upload_folder():
    """Ensure upload folder exists, create if necessary"""
    try:
        upload_path = app.config["UPLOAD_FOLDER"]
        if not os.path.exists(upload_path):
            os.makedirs(upload_path, exist_ok=True)
            print(f"Created upload folder: {upload_path}")
        return True
    except Exception as e:
        print(f"Warning: Could not create upload folder: {e}")
        # In cloud environments, this might be expected if using cloud storage
        return False


# Initialize upload folder (skip in Vercel serverless environment)
if not os.environ.get("VERCEL"):
    ensure_upload_folder()


# ------------------- Middleware -------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Login required.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# ------------------- Auth Routes -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # Get users from configuration
    HARDCODED_USERS = app.config["ADMIN_USERS"]

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = HARDCODED_USERS.get(username)

        if user and user["password"] == password:
            session["user"] = username
            session["user_id"] = user["id"]
            flash("Login successful!", "login")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Try again.", "login")

    categories = [cat for cat, msg in get_flashed_messages(with_categories=True)]
    return render_template("login.html", flash_categories=json.dumps(categories))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Username doesn't exist", "danger")
            return redirect(url_for("forgot_password"))

        token = serializer.dumps(username, salt="reset-password")
        reset_url = url_for("reset_password", token=token, _external=True)
        print(f"[RESET LINK] {reset_url}")
        flash("Reset link sent! Check console (dev mode).", "info")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        username = serializer.loads(token, salt="reset-password", max_age=3600)
    except BadSignature:
        flash("Invalid or expired link", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_pass = request.form["password"]
        hashed = generate_password_hash(new_pass)
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = hashed
            db.session.commit()
            flash("Password updated! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", username=username)


# ------------------- Health Check -------------------
@app.route("/health")
def health_check():
    """Health check endpoint for cloud platforms"""
    try:
        # Test database connection
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return (
            jsonify(
                {
                    "status": "healthy",
                    "database": "connected",
                    "platform": (
                        "vercel"
                        if os.environ.get("VERCEL")
                        else "render" if os.environ.get("RENDER") else "other"
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(e),
                    "platform": (
                        "vercel"
                        if os.environ.get("VERCEL")
                        else "render" if os.environ.get("RENDER") else "other"
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            503,
        )


# ------------------- Main Routes -------------------
@app.route("/")
@login_required
def home():
    return render_template("add_file.html", username=session.get("user"))


@app.route("/search")
@login_required
def search_page():
    return render_template("search_file.html")


@app.route("/add", methods=["POST"])
@login_required
def add_file():
    data = request.form
    existing = File.query.filter_by(file_code=data["file_code"]).first()
    if existing:
        flash("Duplicate file code.", "danger")
    else:
        new_file = File(
            filename=data["filename"],
            file_code=data["file_code"],
            tags=data.get("tags", ""),
            cabinet=data.get("cabinet", ""),
            shelf=data.get("shelf", ""),
            box=data.get("box", ""),
            filepath="",
            user_id=session["user_id"],
        )
        db.session.add(new_file)
        db.session.commit()
        flash("File added successfully!", "success")
    return redirect(url_for("home"))


@app.route("/edit_file/<file_code>", methods=["GET", "POST"])
@login_required
def edit_file(file_code):
    file = File.query.filter_by(file_code=file_code).first()
    if not file:
        flash("File not found.", "danger")
        return redirect(url_for("search_page"))

    if request.method == "POST":
        file.filename = request.form["filename"]
        file.tags = request.form["tags"]
        file.cabinet = request.form["cabinet"]
        file.shelf = request.form["shelf"]
        file.box = request.form["box"]
        db.session.commit()
        flash("File updated successfully!", "success")
        return redirect(url_for("search_page"))

    return render_template("edit_file.html", file=file)


@app.route("/api/search")
@login_required
def search():
    query = request.args.get("q", "").lower()
    results = File.query.filter(
        or_(File.filename.ilike(f"%{query}%"), File.file_code.ilike(f"%{query}%"))
    ).all()
    return jsonify(
        [
            {
                "filename": f.filename,
                "file_code": f.file_code,
                "tags": f.tags,
                "location": f"{f.cabinet} > {f.shelf} > {f.box}",
            }
            for f in results
        ]
    )


@app.route("/export")
@login_required
def export_excel():
    try:
        files = File.query.all()
        df = pd.DataFrame(
            [
                {
                    "filename": f.filename,
                    "file_code": f.file_code,
                    "tags": f.tags,
                    "cabinet": f.cabinet,
                    "shelf": f.shelf,
                    "box": f.box,
                }
                for f in files
            ]
        )

        # For Vercel, use /tmp directory
        if os.environ.get("VERCEL"):
            upload_path = "/tmp"
            os.makedirs(upload_path, exist_ok=True)
        else:
            # Ensure upload folder exists
            if not ensure_upload_folder():
                flash("Error: Upload folder not accessible.", "danger")
                return redirect(url_for("home"))
            upload_path = app.config["UPLOAD_FOLDER"]

        path = os.path.join(upload_path, "exported_files.xlsx")
        df.to_excel(path, index=False)
        return send_file(path, as_attachment=True)
    except Exception as e:
        print(f"Export error: {e}")
        flash("Error exporting files. Please try again.", "danger")
        return redirect(url_for("home"))


@app.route("/import", methods=["POST"])
@login_required
def import_excel():
    file = request.files.get("excel_file")
    if not file or not file.filename.endswith(".xlsx"):
        flash("Invalid file type. Please upload a .xlsx Excel file.", "danger")
        return redirect(url_for("home"))

    try:
        # For Vercel, use /tmp directory
        if os.environ.get("VERCEL"):
            upload_path = "/tmp"
            os.makedirs(upload_path, exist_ok=True)
        else:
            # Ensure upload folder exists
            if not ensure_upload_folder():
                flash("Error: Upload folder not accessible.", "danger")
                return redirect(url_for("home"))
            upload_path = app.config["UPLOAD_FOLDER"]

        filepath = os.path.join(upload_path, secure_filename(file.filename))
        file.save(filepath)
    except Exception as e:
        print(f"File save error: {e}")
        flash("Error saving uploaded file. Please try again.", "danger")
        return redirect(url_for("home"))

    try:
        df = pd.read_excel(filepath)
        df.columns = [col.lower() for col in df.columns]
        required_cols = {"filename", "file_code", "cabinet", "box", "shelf"}
        if not required_cols.issubset(set(df.columns)):
            flash(f"Excel must contain columns: {', '.join(required_cols)}", "danger")
            return redirect(url_for("home"))

        added_count = 0
        for _, row in df.iterrows():
            file_code = str(row.get("file_code")).strip()
            if not file_code:
                continue

            if not File.query.filter_by(file_code=file_code).first():
                new_file = File(
                    filename=row.get("filename", ""),
                    file_code=file_code,
                    tags=row.get("tags", ""),
                    cabinet=row.get("cabinet", ""),
                    shelf=row.get("shelf", ""),
                    box=row.get("box", ""),
                    filepath="",
                    user_id=session["user_id"],
                )
                db.session.add(new_file)
                added_count += 1

        db.session.commit()
        flash(f"Imported {added_count} new files successfully!", "success")
    except Exception as e:
        print(f"[IMPORT ERROR] {e}")
        flash(
            "Error processing Excel file. Check the file format and try again.",
            "danger",
        )

    return redirect(url_for("home"))


# ------------------- Recycle Bin Routes -------------------
@app.route("/delete_file", methods=["POST"])
@login_required
def delete_file():
    data = request.get_json()
    file = File.query.filter_by(file_code=data["file_code"]).first()

    if not file:
        return jsonify({"error": "File not found"}), 404

    recycled = RecycleBin(
        file_code=file.file_code,
        filename=file.filename,
        filepath=file.filepath,
        tags=file.tags,
        cabinet=file.cabinet,
        shelf=file.shelf,
        box=file.box,
        user_id=file.user_id,
    )
    db.session.add(recycled)
    db.session.delete(file)
    db.session.commit()

    return jsonify({"message": f'File "{file.filename}" moved to Recycle Bin'}), 200


@app.route("/recycle_bin", methods=["GET"])
@login_required
def get_recycle_bin():
    files = (
        RecycleBin.query.filter_by(user_id=session["user_id"])
        .order_by(RecycleBin.deleted_at.desc())
        .all()
    )
    return jsonify(
        [
            {
                "file_code": f.file_code,
                "filename": f.filename,
                "deleted_at": f.deleted_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for f in files
        ]
    )


@app.route("/restore_file", methods=["POST"])
@login_required
def restore_file():
    data = request.get_json()
    file_code = data.get("file_code")
    item = RecycleBin.query.filter_by(
        file_code=file_code, user_id=session["user_id"]
    ).first()

    if not item:
        return jsonify({"error": "File not found in Recycle Bin"}), 404

    restored = File(
        file_code=item.file_code,
        filename=item.filename,
        filepath=item.filepath,
        tags=item.tags,
        cabinet=item.cabinet,
        shelf=item.shelf,
        box=item.box,
        user_id=item.user_id,
    )
    db.session.add(restored)
    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": f'File "{item.filename}" restored successfully'}), 200


@app.route("/empty_recycle_bin", methods=["DELETE"])
@login_required
def empty_recycle_bin():
    data = request.get_json()
    file_code = data.get("file_code")

    if file_code:
        deleted = RecycleBin.query.filter_by(
            file_code=file_code, user_id=session["user_id"]
        ).delete()
        msg = (
            f'File "{file_code}" permanently deleted.' if deleted else "File not found."
        )
    else:
        RecycleBin.query.filter_by(user_id=session["user_id"]).delete()
        msg = "Recycle Bin emptied successfully."

    db.session.commit()
    return jsonify({"message": msg}), 200


# ------------------- Init -------------------
def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        try:
            # Test database connection first
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            db.session.commit()

            # Create tables
            db.create_all()
            print("Database tables created successfully")
            return True
        except Exception as e:
            print(f"Error creating database tables: {e}")
            print("Make sure DATABASE_URL is correctly configured")
            # In Vercel, don't fail completely if database isn't ready
            if os.environ.get("VERCEL"):
                print("Running in Vercel environment - database may not be ready yet")
            return False


if __name__ == "__main__":
    create_tables()
    # Get port from environment variable for cloud deployment
    try:
        port = int(os.environ.get("PORT", 5000))
    except (ValueError, TypeError):
        print(f"Invalid PORT value: {os.environ.get('PORT')}, using default 5000")
        port = 5000

    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
else:
    # For production deployment (gunicorn, etc.)
    create_tables()
