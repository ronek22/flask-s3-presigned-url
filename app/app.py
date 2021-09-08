import config
from s3 import AwsS3UploadClass
from flask_wtf import FlaskForm
from wtforms import FileField
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for
import requests
import os
import logging
from uuid import uuid4

logging.basicConfig(level=logging.DEBUG,
                   format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                   datefmt='%Y-%m-%d %H:%M:%S',
                   handlers=[logging.StreamHandler()])

logger = logging.getLogger()


def create_app():
    logger.info(f'Starting app in {config.APP_ENV} environment')
    app = Flask(__name__)
    app.config.from_object('config')
    

    class FileForm(FlaskForm):
        file = FileField("File")

    @app.get("/s3/health")
    def health():
        return {"health": "ok"}, 200


    @app.get("/s3")
    def index():
        form = FileForm()
        return render_template("form.html", form=form)

    @app.post('/s3')
    def upload_file():
        form = FileForm()
        file = None
        if "file" in request.files:
            file = request.files['file']
        else:
            return jsonify(error="requires file")

        s3 = AwsS3UploadClass(app.config['AWS_ID_KEY'], app.config['AWS_SECRET_KEY'], app.config['AWS_S3_BUCKET'])
        key = f"{str(uuid4())}_{file.filename}"
        file.save(key)
        response = s3.create_presigned_post(key)
        if response is None:
            flash('Cannot create presigned post url', 'error')
            return render_template('form.html', form=form)

        files = [('file', open(key, 'rb'))]
        upload_response = requests.post(response['url'], data=response['fields'], files=files)
        os.remove(key)

        if upload_response.status_code == 204:
            flash(f'Succesfully uploaded file: {key}', 'success')
        else:
            flash('Error: file was not uploaded', 'error')
        return redirect(url_for('index'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)