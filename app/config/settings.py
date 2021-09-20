from os import urandom

class BaseConfig():
    AWS_ID_KEY = None
    AWS_SECRET_KEY = None
    AWS_S3_BUCKET = None
    TESTING = False
    DEBUG = False
    SECRET_KEY = urandom(32)
    DB_APP_URL = 'localhost'

class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True

class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'

class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True