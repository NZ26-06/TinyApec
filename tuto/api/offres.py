from flask import Flask, jsonify, request, url_for, abort
from tuto.app import db
from flask import make_response
from tuto.api.errors import bad_request, error_response
from tuto.api import bp
from tuto import models
from tuto.models import Entreprise, Offre, User, Candidate, Offre, Categorie, get_EntrepriseNameByOffreId
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from datetime import date
from tuto.api.auth import token_auth

@bp.route('/offres', methods=['GET'])
def get_offres():
    result = {}
    data_result= {}
    data = Offre.query.limit(240).all()
    data = Offre.listtri(data)
    parsedata = request.get_json() or {}
    if ('reverse' in parsedata):
        key_reverse=parsedata['reverse'].upper()
        if key_reverse == 'TRUE':
            data = Offre.listtri_reverse(data)
    i = 1
    for x in data:
        data_result['title'] = x.title
        data_result['salary'] = x.salary
        data_result['contact'] = x.contact
        # pour de la lisibilite je desactive la description
        # data_result['description'] = x.description
        data_result['dd'] = x.dd
        data_result['dl'] = x.dl
        data_result['contact'] = x.contact
        data_result['entreprise_id'] = x.entreprise_id
        data_result['entreprise_name'] = Entreprise.get_entrepriseNamebyId(x.entreprise_id)
        data_result['categorie_id'] = x.categorie_id
        data_result['categorie_name'] = Categorie.get_CategorieName(x.categorie_id)
        result[i]= data_result
        data_result= {}
        i = i + 1
    # on envoi code 200 avec la liste
    response = jsonify(result)
    response.status_code = 200
    return response



@bp.route('/offres/<int:id>', methods=['GET'])
def get_offre(id):
    # Par defaut si l id n est pas trouve, on renvoi 404. Si il est trouve on envoi code 200 avec l enreistrement
    response = jsonify(Offre.query.get_or_404(id).to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_offre', id=id)
    return response



@bp.route('/offres', methods=['POST'])
@token_auth.login_required
def create_offre():
    data = request.get_json() or {}
    # verification si l offre existe deja
    if ('title' in data) and ('salary' in data) and ('contact' in data) and ('description' in data)  and ('categorie_id' in data) and ('entreprise_id' in data) and ('dd' in data) :
        if ( (Offre.query.filter_by(title=data['title']).first()) and (Offre.query.filter_by(contact=data['contact']).first()) and (Offre.query.filter_by(salary=data['salary']).first()) ):
            #Offre et contact déja existants, forte probabilite de duplicat: code 409
            return error_response(409, 'same title, salary and contact manager as other offre. Please modify to avoid duplicates')
    else:
        return bad_request('must include title, salary, description, dd: depot date of offre, dl: limite date of offre, categorie_id and entreprise_id fields')
    # Pour créér une offre, il faut appartenir a cette meme company ou etre root
    # l USER cree une offre pour une autre société que la sienne
    if (((token_auth.current_user()).company == Entreprise.get_entrepriseNamebyId(int(data['entreprise_id']))) or (token_auth.current_user().id == User.get_UserId('root'))) :
        offre = Offre()
        #il s agit d une nouvelle offre, renvoi code 201 avec location de l enregistrement
        for field in ['title', 'salary', 'contact', 'description', 'categorie_id', 'entreprise_id']:
                if field in data:
                    setattr(offre, field, data[field])
        try:
            offre.dd = datetime.strptime(data['dd'], '%Y%m%d')
        except:
            offre.dd = date.today()
        try:
            offre.dl = datetime.strptime(data['dl'], '%Y%m%d')
        except:
            # si dl absent, on genere une erreur et on rajoute 12 mois
            offre.dl = date.today()+ relativedelta(months=12)
        #offre.from_dict(data, new_offre=True)
        db.session.add(offre)
        db.session.commit()
        # on envoi code 201 avec l enregistrement
        response = jsonify(offre.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('api.get_offre', id=offre.id)
        return response
    else:
        abort(403)




@bp.route('/offres/<int:id>', methods=['PATCH'])
@token_auth.login_required
def update_offre(id):
    #l offre existe ou pas
    offre = Offre.query.get_or_404(id)

    #Uniquement accès pour root ou l auteur meme company que l offre
    if ((token_auth.current_user().company == get_EntrepriseNameByOffreId(id)) or (token_auth.current_user().id == User.get_UserId('root'))) :
        # L id donné correspond à l'état des registres, sinon 404
        # je ne prends pas en charge la creation de ressource si l id n existe pas
        data = request.get_json() or {}
        if (('entreprise_id' in data and (int(data['entreprise_id'])!=offre.entreprise_id))) :
                #l entreprise ne peut etre changé: code 403
                # tous les autres champs peuvent etre update
                return error_response(403, 'cannot change entreprise field')
        # L' update est valide, je remplace tout la ressource: ce n est pas un PATCH
        for field in ['title', 'salary', 'contact', 'description', 'categorie_id']:
                if field in data:
                    setattr(offre, field, data[field])
        if ('dd' in data):
            try:
                offre.dd = datetime.strptime(data['dd'], '%Y%m%d')
            except:
                offre.dd = date.today()
        if ('dl' in data):
            try:
                offre.dl = datetime.strptime(data['dd'], '%Y%m%d')
            except:
                offre.dl = date.today()+ relativedelta(months=6)
        #offre.from_dict(data, new_offre=False)
        db.session.commit()
        # on envoi code 200 avec l enregistrement
        response = jsonify(offre.to_dict())
        response.status_code = 200
        response.headers['Location'] = url_for('api.get_offre', id=offre.id)
        return response
    else:
        abort(403)


@bp.route('/offres/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_offre(id):
    #l offre existe ou pas
    offre = Offre.query.get_or_404(id)
    #Uniquement accès pour root ou l auteur meme company que l offre
    if ((token_auth.current_user().company == get_EntrepriseNameByOffreId(id)) or (token_auth.current_user().id == User.get_UserId('root'))) :
        # L id donné correspond à l'état des registres, sinon 404
        print(Offre.query.filter(Offre.id==int(bid)))
        print(User.query.filter(User.company==  Entreprise.get_entrepriseNamebyId(get_EntrepriseNameByOffreId(id))))
        if (offre.delete_O(offre.id) == 1):
            # L opération a réussi, pas de body pour un delete
            return '', 204
        else:
            # En cas, ou la methode ne peut se faire ou qu'elle n est pas dans les cas 204 et 404
            abort(500)
    else:
        abort(403)
