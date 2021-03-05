from flask import Flask, jsonify, request, url_for, abort
from tuto.app import db
from flask import make_response
from tuto.api.errors import bad_request, error_response
from tuto.api import bp
from tuto import models
from tuto.models import Entreprise, Offre, User, Candidate, Categorie
from tuto.api.auth import token_auth



@bp.route('/categories', methods=['GET'])
def get_categories():
    result = {}
    data_result= {}
    data = Categorie.query.limit(240).all()
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


@bp.route('/categories/<int:id>/offres', methods=['GET'])
def get_offres_by_categorie(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = (Categorie.query.get_or_404(id).to_dict())
    result = {}
    data_result= {}
    results = Offre.query.filter(Offre.categorie_id==response['id']).all()
    i = 1
    for x in results:
        data_result['id Offre']= x.id
        data_result['title']= x.title
        data_result['company']= Entreprise.get_entrepriseNamebyId(id)
        result[i]= data_result
        data_result= {}
        i = i + 1
    # on envoi code 200 avec la liste
    response = jsonify(result)
    response.status_code = 200
    return response




@bp.route('/categories/<int:id>', methods=['GET'])
def get_categorie(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Categorie.query.get_or_404(id).to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_categorie', id=id)
    return response



@bp.route('/categories', methods=['POST'])
@token_auth.login_required
def create_categorie():
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        data = request.get_json() or {}
        # verification si la categorie existe deja
        if ('name' not in data):
            return bad_request('must include name for category')
        if Categorie.query.filter_by(name=data['name']).first():
            #name proposé est déja pris: code 409
            return error_response(409, 'please use a different name for category')
        categorie = Categorie()
        #il s agit d un nouveau category, renvoi code 201 avec location de l enregistrement
        categorie.from_dict(data)
        db.session.add(categorie)
        db.session.commit()
        # on envoi code 201 avec l enregistrement
        response = jsonify(categorie.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.get_categorie', id=categorie.id)
        return response



@bp.route('/categories/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_categorie(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        # je ne prends pas en charge la creation de ressource si l id n existe pas
        categorie = Categorie.query.get_or_404(id)
        data = request.get_json() or {}
        if 'name' in data and data['name'] != categorie.name and Categorie.query.filter_by(name=data['name']).first():
                #name proposé est déja pris: code 409
                return error_response(409, 'please use a different name')
        # L' update est valide, je remplace tout la ressource: ce n est pas un PATCH
        categorie.from_dict(data)
        db.session.commit()
        # on envoi code 200 avec l enregistrement
        response = jsonify(categorie.to_dict())
        response.status_code = 200
        response.headers['Location'] = url_for('api.get_categorie', id=categorie.id)
        return response


@bp.route('/categories/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_categorie(id):
    #Uniquement accès pour root
    if token_auth.current_user().id != User.get_UserId('root') :
        abort(403)
    else:
        # L id donné correspond à l'état des registres, sinon 404
        categorie = Categorie.query.get_or_404(id)
        if (categorie.delete_Cat(categorie.id) == 1):
            # L opération a réussi, pas de body pour un delete
            return '', 204
        else:
            print(categorie.delete_Cat(categorie.id))
            # En cas, ou la methode ne peut se faire ou qu'elle n est pas dans les cas 204 et 404
            abort(500)
