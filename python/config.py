import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost/flask"
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='Flasky Admin <******@qq.com>'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
    AESKEY = '6c13d026mysqlod1'
    @staticmethod
    def init_app(app):
        pass
class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER='smtp.googlemail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:root@localhost/flask"
class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:root@localhost/flask"
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:root@localhost/flask"


config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig,
    'aeskey':'6c13d026mysqlod1',
}