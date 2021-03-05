from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from tuto.models import User
from tuto.api.errors import error_response
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import sha256


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    m = sha256()
    m.update(password.encode())
    if (user and user.password==m.hexdigest()):
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
