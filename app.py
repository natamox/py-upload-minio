from flask import Flask, request, jsonify
import minio
import os

app = Flask(__name__)

# 从环境变量中获取MinIO配置
minio_conf = {
    'endpoint': os.getenv('MINIO_ENDPOINT', ''),
    'access_key': os.getenv('MINIO_ACCESS_KEY', ''),
    'secret_key': os.getenv('MINIO_SECRET_KEY', ''),
    'secure': os.getenv('MINIO_SECURE', 'False') == 'True'
}

UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    # 不限制文件类型
    return True

def get_minio_client():
    return minio.Minio(**minio_conf)

def get_presigned_url(client, bucket_name, object_name, expires=3600):
    try:
        # 获取带签名的URL，这里设置有效时间为1小时(3600秒)
        presigned_url = client.presigned_get_object(
            bucket_name,
            object_name,
            expires
        )
        return presigned_url
    except Exception as e:
        print(e)
        return None

def get_file_url(bucket_name, object_name):
    base_url = "http://" + minio_conf['endpoint'] if not minio_conf['secure'] else "https://" + minio_conf['endpoint']
    return f"{base_url}/{bucket_name}/{object_name}"

@app.route('/upload', methods=['POST'])
def upload_file():
    bucket_name = request.args.get('bucket', 'natamox')
    print(bucket_name)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        client = get_minio_client()
        try:
            client.fput_object(
                bucket_name=bucket_name,
                object_name=filename,
                file_path=file_path,
                content_type='application/octet-stream'
            )
            
            # 获取预签名的URL 有 bug
            # signed_file_url = get_presigned_url(client, bucket_name, filename)
            file_url = get_file_url(bucket_name, filename)

            os.remove(file_path)
            
            if file_url:
                return jsonify({'url': file_url}), 200
            else:
                return jsonify({'error': 'Failed to generate pre-signed URL'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File type not allowed'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)