@app.route("/end-session", methods=["POST"])
def end_session():
    # Delete all uploaded files
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            os.remove(file_path)
        except:
            pass

    # Delete QR if exists
    qr_path = os.path.join(QR_FOLDER, "qr.png")
    if os.path.exists(qr_path):
        os.remove(qr_path)

    return render_template(
        "index.html",
        message="Session ended. You can start a new transfer.",
        qr_image=False,
        files=[]
    )
