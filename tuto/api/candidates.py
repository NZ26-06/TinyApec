from flask import Flask, jsonify, request, url_for, abort
from tuto.app import db
from flask import make_response
from tuto.api.errors import bad_request, error_response
from tuto.api import bp
from tuto import models
from tuto.models import Entreprise, Offre, User, Candidate
from tuto.api.auth import token_auth


@bp.route('/candidates', methods=['GET'])
def get_candidates():
    result = {}
    data_result= {}
    data = Candidate.query.limit(240).all()
    i = 1
    for x in data:
        data_result['username'] = x.username
        data_result['email'] = x.email
        result[i]= data_result
        data_result= {}
        i = i + 1
    # on envoi code 200 avec la liste
    response = jsonify(result)
    response.status_code = 200
    return response



@bp.route('/candidates/<int:id>', methods=['GET'])
def get_candidate(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Candidate.query.get_or_404(id).to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_candidate', id=id)
    return response



@bp.route('/candidates', methods=['POST'])
def create_candidate():
    data = request.get_json() or {}
    # verification si le candidat existe deja: basé sur email
    if ('username' in data) and ('email' in data) and ('password' in data):
        if Candidate.query.filter_by(email=data['email']).first():
            #l email proposé est déja pris: code 409
            return error_response(409,'please use a different email address')
    else:
        return bad_request('must include username, email and password fields')
    candidate = Candidate()
    #il s agit d un nouveau utilisateur, renvoi code 201 avec location de l enregistrement
    candidate.from_dict(data, new_user=True)
    db.session.add(candidate)
    db.session.commit()
     # on envoi code 201 avec l enregistrement
    response = jsonify(candidate.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_candidate', id=candidate.id)
    return response



@bp.route('/candidates/<int:id>', methods=['PATCH'])
def update_candidate(id):
    # L id donné correspond à l'état des registres, sinon 404
    # je ne prends pas en charge la creation de ressource si l id n existe pas
    candidate = Candidate.query.get_or_404(id)
    data = request.get_json() or {}
    # l utilisateur peut tout changer, mais ne pas prendre un email deja existant
    if (('email' in data) and (data['email'] != candidate.email) and (Candidate.query.filter_by(email=data['email']).first())):
            #l email proposé est déja pris: code 409
            return error_response(409, 'Email already in use')
    # L' update est valide, je remplace tout la ressource: ce n est pas un PATCH
    candidate.from_dict(data, new_user=False)
    db.session.commit()
    # on envoi code 200 avec l enregistrement
    response = jsonify(candidate.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_candidate', id=candidate.id)
    return response


@bp.route('/candidates/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_candidate(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        candidate = Candidate.query.get_or_404(id)
        if (candidate.delete_C(candidate.id) == 1):
            # L opération a réussi, pas de body pour un delete
            return '', 204
        else:
            # En cas, ou la methode ne peut se faire ou qu'elle n est pas dans les cas 204 et 404
            abort(500)
