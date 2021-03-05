from flask import Flask
from flask_login import LoginManager


app = Flask(__name__)



login_manager = LoginManager(app)
login_manager.login_view = "login"

app.config['MAX_CONTENT_LENGTH'] = 2048 * 2048
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['UPLOAD_PATH'] = 'tuto/static/images'

import os.path

from flask_bootstrap import Bootstrap
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL']=True


def mkpath(p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__),
            p))

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI']= (
    'sqlite:///'+mkpath('../myapp.db'))
db = SQLAlchemy(app)

from tuto.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')
