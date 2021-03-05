from flask import Flask


from flask import Blueprint
bp = Blueprint('api', __name__)

from tuto.api import candidates, errors, categories, entreprises, offres, users, auth, tokens
