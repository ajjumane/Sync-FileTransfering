from flask import Flask, render_template, request, send_from_directory, abort
import qrcode
import os
import tempfile
import shutil
import atexit
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = tempfile.mkdtemp(prefix="session_uploads_")
QR_FOLDER = "/tmp"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


# ---------------- UTILS ----------------
def is_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ---------------- QR SERVE ----------------
@app.route("/qr.png")
def serve_qr():
    return send_from_directory(QR_FOLDER, "qr.png")


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    qr_image = False

    if request.method == "POST":
        files = request.files.getlist("file")

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        message = "Files uploaded successfully"

        public_url = request.url_root.rstrip("/")

        qr_path = os.path.join(QR_FOLDER, "qr.png")
        qrcode.make(public_url).save(qr_path)

        qr_image = True

    files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))

    return render_template(
        "index.html",
        message=message,
        qr_image=qr_image,
        files=files
    )


# ---------------- VIEW FILE (FOR THUMBNAILS) ----------------
@app.route("/view/<filename>")
def view_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=False
    )


# ---------------- SINGLE FILE DOWNLOAD ----------------
@app.route("/uploads/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# ---------------- DOWNLOAD ALL ----------------
@app.route("/download-all")
def download_all():
    zip_path = os.path.join(app.config["UPLOAD_FOLDER"], "all_files.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
            if filename != "all_files.zip":
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                zipf.write(file_path, arcname=filename)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        "all_files.zip",
        as_attachment=True
    )


# ---------------- CLEANUP ----------------
def cleanup():
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)

atexit.register(cleanup)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
