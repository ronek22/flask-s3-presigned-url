import logging
import os

import boto3
import requests
from botocore.client import Config
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

import config
from s3 import AwsS3UploadClass

logging.basicConfig(level=logging.ERROR,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger()

APP_VERSION = "0.2.0"


def create_app():
    logger.info(f'Starting app in {config.APP_ENV} environment')
    app = Flask(__name__)
    app.config.from_object('config')

    def get_s3_objects():
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket = s3.Bucket(config.AWS_S3_BUCKET)
        bucket_list = bucket.objects.all()
        s3_client = session.client('s3', config=Config(signature_version='s3v4'))
        bucket_with_urls = [(obj, s3_client.generate_presigned_url('get_object',
                                                                   Params={'Bucket': config.AWS_S3_BUCKET, 'Key': obj.key},
                                                                   ExpiresIn=60)) for obj in bucket_list]
        return bucket_with_urls

    def sanitize_filename(filename: str):
        for sep in ('/', '\\'):
            if sep in filename:
                filename = filename.split(sep)[-1]
        filename = secure_filename(filename)
        return filename

    def parse_url(url: str) -> str:
        if 'http' not in url:
            url = f"http://{url}"
        return url

    def fetch_from_db_app() -> dict:
        try:
            base_url = parse_url(config.DB_APP_URL)
            total = requests.get(f"{base_url}/db/total", timeout=5)
            result = total.json()
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError) as e:
            result = {"status": 400, "error": str(e)}
        except Exception as e:
            result = {"status": 400, "error": str(e)}
        return result

    @app.get("/s3/health")
    def health():
        return {"health": "ok"}, 200

    @app.get("/s3")
    def index():
        object_list = get_s3_objects()
        data_from_db_app = fetch_from_db_app()

        return render_template("form.html", db=data_from_db_app, object_list=object_list, bucket=config.AWS_S3_BUCKET,
                               version=APP_VERSION)

    @app.get("/s3/presigned_url")
    def upload_url():
        filename = sanitize_filename(request.args.get('upload_file'))
        s3 = AwsS3UploadClass(config.AWS_S3_BUCKET)
        upload_data = s3.create_presigned_post(filename)
        return jsonify(upload_data)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
