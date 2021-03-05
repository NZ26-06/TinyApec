from flask import Flask, jsonify, request, url_for, abort
from tuto.app import db
from flask import make_response
from tuto.api.errors import bad_request, error_response
from tuto.api import bp
from tuto import models
from tuto.models import Entreprise, Offre, User, Candidate, Categorie, Entreprise
from tuto.api.auth import token_auth


@bp.route('/entreprises', methods=['GET'])
def get_enterprises():
    result = {}
    data_result= {}
    data = Entreprise.query.limit(240).all()
    i = 1
    for x in data:
        data_result['name'] = x.name
        result[i]= data_result
        data_result= {}
        i = i + 1
    # on envoi code 200 avec la liste
    response = jsonify(result)
    response.status_code = 200
    return response


@bp.route('/entreprises/<int:id>/offres', methods=['GET'])
def get_offre_by_entreprise(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Entreprise.query.get_or_404(id).to_dict())
    data_result={}
    result = {}
    #renvoi liste des offres par id de cette entreprise
    response_offre = Entreprise.get_entreprise_offres(id)
    i = 1
    for x in response_offre:
        data_result['title']= x.title
        data_result['offre id']= x.id
        result[i]= data_result
        data_result= {}
        i = i + 1
    response = jsonify(result)
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_entreprise', id=id)
    return response



@bp.route('/entreprises/<int:id>/users', methods=['GET'])
def get_user_by_entreprise(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Entreprise.query.get_or_404(id).to_dict())
    result = {}
    company_name= Entreprise.get_entrepriseNamebyId(id)
    user = User.query.filter(User.company==company_name).all()[0]
    result['id User']=user.id
    result['username']=user.username
    result['company']=user.company
    response = jsonify(result)
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response



@bp.route('/entreprises/<int:id>', methods=['GET'])
def get_entreprise(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Entreprise.query.get_or_404(id).to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_entreprise', id=id)
    return response



@bp.route('/entreprises', methods=['POST'])
@token_auth.login_required
def create_entreprise():
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        data = request.get_json() or {}
        # verification si le candidat existe deja
        if ('name' not in data):
            return bad_request('must include name for entreprise')
        if Entreprise.query.filter_by(name=data['name']).first():
            #name proposé est déja pris: code 409
            return error_response(409, 'please use a different name for entreprirse')
        entreprise = Entreprise()
        #il s agit d une nouvelle entreprise, renvoi code 201 avec location de l enregistrement
        entreprise.from_dict(data)
        db.session.add(entreprise)
        db.session.commit()
        # on envoi code 201 avec l enregistrement
        response = jsonify(entreprise.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.get_entreprise', id=entreprise.id)
        return response



@bp.route('/entreprises/<int:id>', methods=['PATCH'])
@token_auth.login_required
def update_entreprise(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        # je ne prends pas en charge la creation de ressource si l id n existe pas
        entreprise = Entreprise.query.get_or_404(id)
        data = request.get_json() or {}
        if 'name' in data and data['name'] != entreprise.name and Entreprise.query.filter_by(name=data['name']).first():
                #name proposé est déja pris: code 409
            return error_response(409, 'please use a different name')
        # L' update est valide, je remplace tout la ressource: ce n est pas un PATCH
        entreprise.from_dict(data)
        db.session.commit()
        # on envoi code 200 avec l enregistrement
        response = jsonify(entreprise.to_dict())
        response.status_code = 200
        response.headers['Location'] = url_for('api.get_entreprise', id=entreprise.id)
        return response


@bp.route('/entreprises/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_entreprise(id):
    #Uniquement accès pour root

    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        entreprise = Entreprise.query.get_or_404(id)
        if (entreprise.delete_E(entreprise.id) == 1):
            return '', 204
        else:
            # En cas, ou la methode ne peut se faire ou qu'elle n est pas dans les cas 204 et 404
            abort(500)
