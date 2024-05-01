import hashlib
from flask import Flask, request, jsonify
from gevent import pywsgi
import minio
import os

app = Flask(__name__)

minio_conf = {
    "endpoint": os.getenv("ENDPOINT", ""),
    "access_key": os.getenv("ACCESS_KEY", ""),
    "secret_key": os.getenv("SECRET_KEY", ""),
    "secure": os.getenv("SECURE", "False") == "True",
}

UPLOAD_TMP_FOLDER = "./tmp"


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_md5(path):
    with open(path, "rb") as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        md5_hash = md5obj.hexdigest()
    return md5_hash


def get_minio_client():
    return minio.Minio(**minio_conf)


def get_file_url(bucket_name, object_name):
    domain = os.getenv("DOMAIN", minio_conf["endpoint"])
    base_url = "http://" + domain if not minio_conf["secure"] else "https://" + domain
    return f"{base_url}/{bucket_name}/{object_name}"


@app.route("/upload", methods=["POST"])
def upload_file():
    bucket_name = request.form.get("bucket", os.getenv("BUCKET"))

    if not bucket_name:
        return jsonify({"error": "No bucket part"})

    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    create_directory_if_not_exists(UPLOAD_TMP_FOLDER)

    if file:
        file_path = os.path.abspath(os.path.join(UPLOAD_TMP_FOLDER, file.filename))
        file_type = None
        if "." in file.filename:
            file_type = "." + file.filename.split(".")[-1]

        file.save(file_path)

        md5 = get_md5(file_path)

        if file_type:
            file_name = md5 + file_type
        else:
            file_name = md5

        client = get_minio_client()

        client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=file_path,
            content_type="application/octet-stream",
        )

        file_url = get_file_url(bucket_name, file_name)

        os.remove(file_path)

        if file_url:
            return jsonify({"url": file_url})
        else:
            return jsonify({"error": "Failed to generate URL"})

    return jsonify({"error": "File type not allowed"})


if __name__ == "__main__":
    server = pywsgi.WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()
