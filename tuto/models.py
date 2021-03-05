import yaml, os.path
from datetime import datetime, time, timedelta
from .app import db
from flask_login import UserMixin
from .app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import base64


#################################### Utils #####################################

@login_manager.user_loader
def load_user(username):
    return User.query.filter(User.username==str(username)).one()

offres = yaml.load( open(
        os.path.join(
            os.path.dirname(__file__),
            "data.yml")), Loader=yaml.FullLoader)



##########################################Cross Objects ###########################""

def get_EntrepriseNameByOffreId(id):
    companyName = (Entreprise.query.filter(Entreprise.id==(Offre.query.filter(Offre.id==id).all())[0].entreprise_id).one()).name
    return companyName

def deletecompany_listoffres_users(name):
    id = Entreprise.get_EntrepriseId(name)
    Entreprise.deleteEntreprise(id)
    totaloffres = Offre.listalloffres()
    for x in totaloffres:
        if (x.entreprise_id ==id):
            deleteOffrebyCompany(x.id)
    for y in User.listallUsers():
        if (y.company == name):
            User.deleteUser(y.username)

def get_corporateList(company):
    corporate = []
    corporate = User.query.filter(User.company==str(company)).all()
    return corporate


def treatmydemand(mysearch, mysalary, mycompany):
    totalresult = []
    for x in mysearch.split():
        if (mycompany != ''):
            mycompanyId = Entreprise.get_EntrepriseId(mycompany)
            total = Offre.query.filter(Offre.description.like('%'+ x +'%')).filter(Offre.entreprise_id==mycompanyId).filter(Offre.salary > mysalary).all()
        else:
            total = Offre.query.filter(Offre.description.like('%'+ x +'%')).filter(Offre.salary > mysalary).all()
        for y in total:
            totalresult.append(y.id)
        total = []
    mylist = list(dict.fromkeys(totalresult))
    return mylist


def insertcandidate(username, password, email):
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    c = Candidate(username=username, password=m.hexdigest(), email=email)
    db.session.add(c)
    db.session.commit()



#################################### Entreprise #####################################
class Entreprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    img = db.Column(db.String(100))




    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
        }
        return data

    def from_dict(self, data):
        for field in ['name']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def get_entreprise_offres(id):
        offrelist = Entreprise.query.get(id).offres.all()
        return offrelist

    # delete avec un retour
    def delete_E(self, id):
        result = Entreprise.query.filter(Entreprise.id==int(id)).delete()
        db.session.commit()
        return result

    # delete sans retour
    @staticmethod
    def deleteEntreprise(bid):
        Entreprise.query.filter(Entreprise.id==int(bid)).delete()
        db.session.commit()

    @staticmethod
    def get_entreprise(id):
        return Entreprise.query.get(id)

    @staticmethod
    def get_EntrepriseId(company):
        companyID = (Entreprise.query.filter(Entreprise.name==company).all())[0].id
        return companyID


    @staticmethod
    def get_EntrepriseLogoById(id):
        companyID = (Entreprise.query.filter(Entreprise.id==id).all())[0].img
        return companyID

    @staticmethod
    def get_EntrepriseLogo(company):
        companyLogo = (Entreprise.query.filter(Entreprise.name==company).all())[0].img
        return companyLogo

    @staticmethod
    def get_entrepriselist():
        elist = Entreprise.query.all()
        return elist

    @staticmethod
    def get_entrepriselistname():
        namelist = []
        namelist.append('')
        elist = Entreprise.query.all()
        for x in elist:
                namelist.append(x.name)
        return namelist

    @staticmethod
    def get_entrepriselist4User():
        dic = []
        alist = Entreprise.query.all()
        for x in alist:
            dic.append(x.name)
        return dic


    @staticmethod
    def get_entrepriseIDbyCompanyName(name):
        result = Entreprise.query.filter(Entreprise.name==name).all()[0].id
        return result

    @staticmethod
    def get_entrepriseNamebyId(id):
        result = Entreprise.query.filter(Entreprise.id==id).all()[0].name
        return result

    def get_id(self):
        return self.name

#################################### User #####################################

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(64))
    company = db.Column(db.String(64))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'username': self.username,
            'company': self.company,
        }
        if include_password:
            data['password'] = self.password
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'company', 'password']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            hashed = self.set_password(data['password'])
            self.password = hashed

    def get_token(self, expires_in=36000):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    def delete_U(self, id):
        result = User.query.filter(User.id==int(id)).delete()
        db.session.commit()
        return result

    #Delete User by name
    @staticmethod
    def deleteUser(name):
        User.query.filter(User.username==str(name)).delete()
        db.session.commit()

    @staticmethod
    def get_userlistname():
        userlist = []
        userlist.append('')
        ulist = User.query.all()
        for x in ulist :
            if (x.username != 'root'):
                user_texte = x.username + "/" + x.company
                userlist.append(user_texte)
        return userlist

    @staticmethod
    def listallUsers():
        lUsers= []
        lUsers = User.query.all()
        return lUsers

    @staticmethod
    def get_UserId(username):
        userID = (User.query.filter(User.username==username).all())[0].id
        return userID

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def get_id(self):
        return self.username

#################################### Candidate#####################################

class Candidate(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(64))
    email = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete_C(self, id):
        result = Candidate.query.filter(Candidate.id==int(id)).delete()
        db.session.commit()
        return result

    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }
        if include_password:
            data['password'] = self.password
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'password']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            hashed = self.set_password(data['password'])
            self.password = hashed

    @staticmethod
    def listcandidates():
        lcandidates = []
        lcandidates = Candidate.query.all()
        return lcandidates

    def get_id(self):
        return self.username

#################################### Categorie #####################################

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(30))

    def delete_Cat(self, id):
        result = Categorie.query.filter(Categorie.id==int(id)).delete()
        db.session.commit()
        return result

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
        }
        return data

    def from_dict(self, data):
        for field in ['name']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def get_CategorieId(categorie):
        categorieID = (Categorie.query.filter(Categorie.name==categorie).all())[0].id
        return categorieID


    @staticmethod
    def get_CategorieName(id):
        categorie_Name = (Categorie.query.filter(Categorie.id==id).all())[0].name
        return categorie_Name

    @staticmethod
    def get_categorielist():
        clist = Categorie.query.all()
        categorie_list = []
        for c in clist:
            categorie_list.append(c.name)
        return categorie_list

    def get_id(self):
        return self.name

#################################### Offre #####################################

class Offre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    salary = db.Column(db.String(20))
    contact=db.Column(db.String(100))
    description=db.Column(db.String(1000))
    dd = db.Column(db.DateTime, default=datetime.utcnow().strftime('%Y-%M-%D'))
    dl = db.Column(db.DateTime, nullable=True)
    entreprise_id = db.Column(db.Integer, db.ForeignKey("entreprise.id"))
    entreprise = db.relationship("Entreprise", backref=db.backref("offres", lazy="dynamic"))
    categorie_id = db.Column(db.Integer, db.ForeignKey("categorie.id"))
    categorie = db.relationship("Categorie", backref=db.backref("offres", lazy="dynamic"))

    def delete_O(self, id):
        result = Offre.query.filter(Offre.id==int(id)).delete()
        print(Offre.query.filter(Offre.id==int(id)))
        db.session.commit()
        return result

    @staticmethod
    def deleteOffre(bid):
        Offre.query.filter(Offre.id==int(bid)).delete()
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'salary': self.salary,
            'contact': self.contact,
            'dd' : self.dd,
            'dl' : self.dl,
            'entreprise_id': self.entreprise_id,
            'categorie_id': self.categorie_id,
            'description': self.description,
        }
        return data


        self.entreprise_id =int(data['entreprise_id'])
        self.categorie_id=int(data['categorie_id'])
        if new_offre:
            self.dd=date.today()
            self.dl=date.today()+ relativedelta(months=6)

    @staticmethod
    def listalloffres():
        loffres= []
        loffres = Offre.query.all()
        return Offre.reject_old_offre(loffres)

    @staticmethod
    def get_title(id):
        title = ""+ Offre.query.get(id).title
        return title

    @staticmethod
    def deleteOffrebyCompany(bid):
        Offre.query.filter(Offre.id==int(bid)).delete()
        db.session.commit()

    @staticmethod
    def get_salary(id):
        salary = Offre.query.get(id).salary
        return salary

    @staticmethod
    def get_offre(id):
        return Offre.query.get(id)

    @staticmethod
    def get_sample():
        offre_sample= Offre.query.limit(240).all()
        offre_sample = Offre.listtri(Offre.reject_old_offre(offre_sample))
        return offre_sample


    @staticmethod
    def listtri(list):
        offre_sample = list
        temp = offre_sample
        offre_sample_croissant = []
        min = datetime.max
        while (len(offre_sample)>0):
            for x in offre_sample:
                if (x.dl < min):
                    min = x.dl
                    min_x = x
            offre_sample_croissant.append(min_x)
            offre_sample.remove(min_x)
            min = datetime.max
        offre_sample = temp
        return offre_sample_croissant

    @staticmethod
    def listtri_reverse(list):
        offre_sample = list
        temp = offre_sample
        offre_sample_decroissant = []
        max = datetime.min
        while (len(offre_sample)>0):
            for x in offre_sample:
                if (x.dl > max):
                    max = x.dl
                    max_x = x
            offre_sample_decroissant.append(max_x)
            offre_sample.remove(max_x)
            max = datetime.min
        offre_sample = temp
        return offre_sample_decroissant

    @staticmethod
    def reject_old_offre(liste):
        for x in liste:
            if (x.dl < datetime.utcnow()):
                liste.remove(x)
        return liste

    def __repr__(self):
        return "<Offre (%d) %s>" % (self.id, self.title)
