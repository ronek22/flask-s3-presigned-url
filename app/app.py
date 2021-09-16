from werkzeug.utils import secure_filename
import config
from s3 import AwsS3UploadClass
from flask_wtf import FlaskForm
from wtforms import FileField
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for
import requests
import os
import logging
import boto3
from uuid import uuid4
from botocore.client import Config

logging.basicConfig(level=logging.ERROR,
                   format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                   datefmt='%Y-%m-%d %H:%M:%S',
                   handlers=[logging.StreamHandler()])

logger = logging.getLogger()

# Outside aws
def create_app():
    logger.info(f'Starting app in {config.APP_ENV} environment')
    app = Flask(__name__)
    app.config.from_object('config')
    

    def get_s3_objects():
        session = boto3.Session(
            aws_access_key_id=config.AWS_ID_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
            region_name='eu-central-1'
        )
        s3 = session.resource('s3')
        bucket = s3.Bucket(config.AWS_S3_BUCKET)
        bucket_list = bucket.objects.all()
        s3_client = session.client('s3', config=Config(signature_version='s3v4'))
        bucket_with_urls = [(obj, s3_client.generate_presigned_url('get_object', Params={'Bucket': config.AWS_S3_BUCKET, 'Key': obj.key}, ExpiresIn=60)) for obj in bucket_list]
        return bucket_with_urls

    def sanitize_filename(filename: str):
        for sep in ('/', '\\'):
            if sep in filename:
                filename = filename.split(sep)[-1]
        filename = secure_filename(filename)
        return filename

    @app.get("/s3/health")
    def health():
        return {"health": "ok"}, 200


    @app.get("/s3")
    def index():
        object_list = get_s3_objects()

        return render_template("form.html", object_list=object_list, bucket=config.AWS_S3_BUCKET)

    @app.get("/s3/presigned_url")
    def upload_url():
        filename = sanitize_filename(request.args.get('upload_file'))
        s3 = AwsS3UploadClass(config.AWS_ID_KEY, config.AWS_SECRET_KEY, config.AWS_S3_BUCKET)
        upload_data = s3.create_presigned_post(filename)
        return jsonify(upload_data)

    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)