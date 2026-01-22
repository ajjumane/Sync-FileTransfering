from flask import Flask, render_template, request, send_from_directory
import qrcode
import socket
import os
import webbrowser
import threading
import tempfile
import shutil
import atexit
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = tempfile.mkdtemp(prefix="session_uploads_")
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        files = request.files.getlist("file")
        for file in files:
            if file and file.filename != "":
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
        message = "Files successfully uploaded"


    # Generate QR code
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    qr_path = os.path.join(STATIC_FOLDER, "qr.png")
    qrcode.make(url).save(qr_path)

    files = os.listdir(UPLOAD_FOLDER)

    return render_template(
        "index.html",
        message=message,
        qr_image="qr.png",
        files=files
    )

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/download-all")
def download_all():
    zip_path = os.path.join(UPLOAD_FOLDER, "all_files.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename != "all_files.zip":
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                zipf.write(file_path, arcname=filename)

    return send_from_directory(
        UPLOAD_FOLDER,
        "all_files.zip",
        as_attachment=True
    )



def open_browser():
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    if os.path.exists(brave_path):
        webbrowser.register(
            "brave",
            None,
            webbrowser.BackgroundBrowser(brave_path)
        )
        webbrowser.get("brave").open_new("http://127.0.0.1:5000")
    else:
        print("Brave browser not found at:", brave_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    
    
def cleanup():
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)

atexit.register(cleanup)


