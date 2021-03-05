from flask import Flask, jsonify, request, url_for, abort
from tuto.app import db
from flask import make_response
from tuto.api.errors import bad_request, error_response
from tuto.api import bp
from tuto import models
from tuto.models import Entreprise, Offre, User, Candidate
from tuto.api.auth import token_auth


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        result = {}
        data_result= {}
        data = User.query.limit(240).all()
        i = 1
        for x in data:
            data_result['username'] = x.username
            data_result['company'] = x.company
            result[i]= data_result
            data_result= {}
            i = i + 1
        # on envoi code 200 avec la liste
        response = jsonify(result)
        response.status_code = 200
        return response



@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
        response = jsonify(User.query.get_or_404(id).to_dict())
        response.status_code = 200
        response.headers['Location'] = url_for('api.get_user', id=id)
        return response



@bp.route('/users', methods=['POST'])
@token_auth.login_required
def create_user():
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        data = request.get_json() or {}
        # verification si le candidat existe deja
        if ('username' in data) and ('company' in data) and ('password' in data):
            if User.query.filter_by(company=data['company']).first():
                # un seul user par company : code 409
                return error_response(409, 'Only one User per company')
        else:
            return bad_request('must include username, company and password fields')
        user = User()
        #il s agit d un nouveau utilisateur, renvoi code 201 avec location de l enregistrement
        user.from_dict(data, new_user=True)
        db.session.add(user)
        db.session.commit()
        # on envoi code 201 avec l enregistrement
        response = jsonify(user.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.get_user', id=user.id)
        return response



@bp.route('/users/<int:id>', methods=['PATCH'])
@token_auth.login_required
def update_user(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        # je ne prends pas en charge la creation de ressource si l id n existe pas
        user = User.query.get_or_404(id)
        data = request.get_json() or {}
        # L' update est valide, je remplace tout la ressource: ce n est pas un PATCH
        user.from_dict(data, new_user=False)
        db.session.commit()
        # on envoi code 200 avec l enregistrement
        response = jsonify(user.to_dict())
        response.status_code = 200
        response.headers['Location'] = url_for('api.get_user', id=user.id)
        return response


@bp.route('/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        user = User.query.get_or_404(id)
        if (user.delete_U(user.id) == 1):
            # L opération a réussi, pas de body pour un delete
            return '', 204
        else:
            # En cas, ou la methode ne peut se faire ou qu'elle n est pas dans les cas 204 et 404
            abort(500)
