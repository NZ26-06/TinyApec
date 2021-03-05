import os
from datetime import datetime
from .app import app
from flask import render_template, request, abort
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length
from .models import get_EntrepriseNameByOffreId, treatmydemand, deletecompany_listoffres_users
from .models import Entreprise, Offre, User, Candidate, Categorie
from wtforms import StringField, HiddenField, SelectField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, InputRequired
from flask import url_for, redirect
from .app import db
from hashlib import sha256
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from .models import insertcandidate


app.config['SECRET_KEY']= "fbc56da3-7935-4a24-ac24-248f4ccd65a4"



class EntrepriseForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])
    contact = StringField('Contact')
    file = FileField('Logo', validators=[FileRequired(), FileAllowed(['jpg','jpeg','png'], 'Images only')])


class OffreForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('Title', validators=[DataRequired()])
    salary = StringField('Price', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    choicename = SelectField('Categories', choices=Categorie.get_categorielist())
    date_c = DateField('Creation Date', format='%Y-%m-%d', validators=[DataRequired()])
    date_l = DateField('Application Limit Date', format='%Y-%m-%d' )

class DateForm(FlaskForm):
    id = HiddenField('id')
    date_c = DateField('Creation Date', format='%Y-%m-%d', validators=[DataRequired()])
    date_l = DateField('Application Limit Date', format='%Y-%m-%d' )

class SearchForm(FlaskForm):
    id = HiddenField('id')
    mysearch = StringField('Your Search',validators=[DataRequired()])
    salary = StringField('Salary')
    choicename = SelectField('Categories', choices=Categorie.get_categorielist())
    choicecompany = SelectField('Entreprises', choices=Entreprise.get_entrepriselistname())
    invert = BooleanField('Decreasing Application Time')

class EntrepriseSearchForm(FlaskForm):
    id = HiddenField('id')
    choicecompany = SelectField('Entreprises', choices=Entreprise.get_entrepriselistname())

class UserSearchForm(FlaskForm):
    id = HiddenField('id')
    choiceuser = SelectField('Users', choices=[1, 2])


class CandiForm(FlaskForm):
    id = HiddenField('id')
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    email = PasswordField('Email',validators=[DataRequired()])
    next = HiddenField()


class LoginForm(FlaskForm):
    id = HiddenField('id')
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()

    def get_authenticated_user(self):
        user = User.query.filter(User.username==str(self.username.data)).one()
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        result= (user if passwd == user.password else None)
        return result


#########################################################################################




@app.route("/delete/offre/<int:id>", methods=("POST",))
@app.route("/delete/offre/<int:id>")
@login_required
def delete_offre(id):
    if ((current_user.company==get_EntrepriseNameByOffreId(id))or(current_user.company=='root')):
        b = Offre.get_offre(id)
        f = OffreForm(title=b.title, salary=b.salary, choicename=b.entreprise_id )
        Offre.deleteOffre(id)
        return redirect(url_for("one_entreprise", id=b.entreprise_id  ))
    else:
        return render_template("Not4You.html")

########################################################################################

@app.route("/edit/offre/<int:id>", methods=("POST",))
@app.route("/edit/offre/<int:id>")
@login_required
def edit_offre(id):
    if ((current_user.company==get_EntrepriseNameByOffreId(id))or(current_user.company=='root')):
        b = Offre.get_offre(id)
        a = b.entreprise_id
        f = OffreForm(title=b.title, salary=b.salary, contact=b.contact, description=b.description )
        if f.validate_on_submit():
            b.title = f.title.data
            b.salary = f.salary.data
            b.contact = f.contact.data
            b.dd = f.date_c.data
            b.dl = f.date_l.data
            b.categorie_id = Categorie.get_CategorieId(f.choicename.data)
            b.description = f.description.data
            db.session.commit()
            return redirect(url_for("one_entreprise", id=a ))
        return render_template("edit_offre.html",offre =b, form=f, templ_id=id, image=Entreprise.get_EntrepriseLogoById(a))
    else :
        return render_template("Not4You.html")
########################################################################################

@app.route("/create/offre", methods=("POST", ))
@app.route("/create/offre")
@login_required
def create_offre():
        f = OffreForm()
        if f.validate_on_submit():
            b = Offre()
            b.title = f.title.data
            b.salary = f.salary.data
            b.contact = f.contact.data
            b.description = f.description.data
            b.dd = f.date_c.data
            b.dl = f.date_l.data
            b.entreprise_id = Entreprise.get_entrepriseIDbyCompanyName(current_user.company)
            b.categorie_id = Categorie.get_CategorieId(f.choicename.data)
            db.session.add(b)
            db.session.commit()
            return redirect(url_for("one_entreprise", id=b.entreprise_id))
        return render_template("create_offre.html", form=f, image=Entreprise.get_EntrepriseLogo(current_user.company))

########################################################################################
@app.route("/edit/entreprise/<int:id>", methods=("POST",))
@app.route("/edit/entreprise/<int:id>")
@login_required
def edit_entreprise(id):
    if ((current_user.company==Entreprise.get_entrepriseNamebyId(id))or(current_user.company=='root')):
        a = Entreprise.get_entreprise(id)
        f = EntrepriseForm(id=a.id, name=a.name)
        if f.validate_on_submit():
            a.name = f.name.data
            handle = f.file.data
            filename = secure_filename(handle.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                handle.save(os.path.join(app.config['UPLOAD_PATH'],filename))
            a.img = filename
            db.session.add(a)
            db.session.commit()
            return redirect(url_for("one_entreprise", id=a.id ))
        return render_template("edit_entreprise.html", entreprise=a, form=f, id=id)
    else:
        return render_template("Not4You.html")


@app.route("/create/entreprise", methods=("POST", ))
@app.route("/create/entreprise")
@login_required
def create_entreprise():
    if ((current_user.company=='Root')):
        id = None
        f = EntrepriseForm()
        if f.validate_on_submit():
            ecrivain = Entreprise(name=f.name.data)
            handle = f.file.data
            filename = secure_filename(handle.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                handle.save(os.path.join(app.config['UPLOAD_PATH'],filename))
            ecrivain.img = filename
            db.session.add(ecrivain)
            db.session.commit()
            return redirect(url_for('one_entreprise', id=ecrivain.id))
        return render_template("create_entreprise.html", form=f)
    else:
        return render_template("Not4You.html")



@app.route("/select/entreprise", methods=("POST", ))
@app.route("/select/entreprise")
@login_required
def select_entreprise():
    if ((current_user.company=='Root')):
        f = EntrepriseSearchForm()
        return render_template("search_entreprise.html", form=f)
    else:
        Entreprise.get_entreprise_offrese("Not4You.html")

##########################################################################
@app.route("/select/user", methods=("POST", ))
@app.route("/select/user")
@login_required
def select_user():
    if ((current_user.company=='Root')):
        f = UserSearchForm('Users', choices=User.get_userlistname())
        return render_template("search_user.html", form=f)
    else:
        return render_template("Not4You.html")


@app.route("/delete/user", methods=("POST", ))
@app.route("/delete/user")
@login_required
def delete_user():
    if ((current_user.company=='root')):
        User.deleteUser(((request.form.get('choiceuser')).split('/'))[0])
        return redirect(url_for('home'))
    else:
        return render_template("Not4You.html")



@app.route("/delete/user/id")
@login_required
def delete_user_id(id):
    if ((current_user.company=='root')):
        User.deleteUser(id)
        return redirect(url_for('home'))
    else:
        return render_template("Not4You.html")
##########################################################################


@app.route("/deletealldata", methods=("POST",))
@login_required
def delete_data_entreprise():
    if ((current_user.company=='Root')):
        company = request.form.get('choicecompany')
        deletecompany_listoffres_users(company)
        return render_template("fakehome.html", texte=company)
    else:
        abort(401)


@app.route("/delete/entreprise/<int:id>")
@login_required
def delete_entreprise(id):
    if ((current_user.company=='root')):
        Entreprise.deleteEntreprise(id)
        return redirect(url_for('home'))
    else:
        return render_template("Not4You.html")



@app.route("/show/entreprise/<int:id>")
def one_entreprise(id):
    a = Entreprise.get_entreprise(id)
    loffres = Entreprise.get_entreprise_offres(id)
    f = EntrepriseForm(id=a.id, name=a.name)
    return render_template( "one_entreprise.html",
      entreprise =a, offres=loffres, form=f
    )

@app.route("/yourentreprise")
def yourentreprise():
    if (current_user.is_authenticated):
        id = Entreprise.get_entrepriseIDbyCompanyName(current_user.company)
        a = Entreprise.get_entreprise(id)
        loffres = Entreprise.get_entreprise_offres(id)
        f = EntrepriseForm(id=a.id, name=a.name)
        return render_template( "one_entreprise.html",
        entreprise =a, offres=loffres, form=f)
    else :
        abort(401)


#######################################################################

@app.route("/listoffres/reverse")
def listoffresreverse():
      myoffres =  Offre.listtri_reverse(Offre.listalloffres())
      return render_template("list_offres_reverse.html", mylist=myoffres)

@app.route("/listoffres")
def listoffres():
      myoffres =  Offre.listtri(Offre.listalloffres())
      return render_template("list_offres.html", mylist=myoffres)

#######################################################################

@app.route("/show/candidate")
@login_required
def show_candidatelist():
    myoffres =  Candidate.listcandidates()
    return render_template("list_candidate.html", mylist=myoffres)


#######################################################################
@app.route("/show/entrepriselist")
def showentrepriselist():
    return render_template(
              "list_entreprise.html", mylist=Entreprise.get_entrepriselist()
          )


#######################################################################

def grant_access4corporate(id):
    if (current_user.is_authenticated ):
        result = ((get_EntrepriseNameByOffreId(id)==current_user.company)or(current_user.company=='root'))
    else:
        result = False
    return result

@app.route("/show/offre/<int:id>")
def show_offre(id):
    b= Offre.get_offre(id)
    f = OffreForm(id=b.id, title=b.title, salary=b.salary, image=(b.entreprise).img, contact=b.contact, description=b.description, date_c=b.dd , date_l=b.dl)
    return render_template(
        "show_offre.html", form=f, offre=b, image=(b.entreprise).img, bol=grant_access4corporate(id) , choicename=Categorie.get_CategorieName(b.categorie_id)
    )


########################################################################################

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


########################################################################################
@app.route("/login", methods=("GET","POST",))
def login():
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            t = login_user(user)
            next = f.next.data or url_for("home")
            if (user.username != 'root'):
                return redirect(url_for('one_entreprise', id=(Entreprise.get_entrepriseIDbyCompanyName(user.company))))
            else:
                return redirect(next)
    return render_template(
        "login.html", form =f
    )


@app.route("/candsignup", methods=("GET","POST",))
def candsignup():
    f = CandiForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        cand_username = f.username.data
        cand_password = f.password.data
        cand_email = f.email.data
        insertcandidate(cand_username,cand_password,cand_email)
        return render_template("done.html")
    return render_template(
        "candsignup.html", form =f
    )

########################################################################################
@app.route("/search", methods=("POST",))
@app.route("/search")
def search():
    f = SearchForm()
    return render_template("mysearch.html", form=f)


@app.route("/result", methods=("POST",))
def result():
    mysearch = request.form.get('mysearch')
    mysalary = request.form.get('salary')
    mycompany = request.form.get('choicecompany')
    resultlistOffer = []
    for x in treatmydemand(mysearch, mysalary, mycompany):
        resultlistOffer.append(Offre.get_offre(x))
    if (request.form.get('invert')=='y'):
        resultlistOffer = Offre.listtri_reverse(resultlistOffer)
    else:
        resultlistOffer = Offre.listtri(resultlistOffer)
    resultlistOffer=Offre.reject_old_offre(resultlistOffer)
    return render_template("myresults.html", mylist=resultlistOffer, mysearch=mysearch, mysalary=mysalary, mycompany=mycompany)


########################################################################################

@app.route("/")
def home():
    return render_template("home.html", title="Tiny Apec" , offres=Offre.get_sample())
#

@app.route('/api/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')
