import click
from .app import app, db
from .models import get_corporateList, Entreprise


@app.cli.command()
def syncdb():
    '''Creates all missing tables'''
    db.create_all()



@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    '''Creates the tables and populates them with data'''
    db.drop_all()
    # creation de toutes les tables
    db.create_all()

    #chargement de notre jeu de donnee
    import yaml
    offres = yaml.load(open(filename), Loader=yaml.SafeLoader)

    # import des modeles
    from .models import Entreprise, Offre, Categorie, Candidate

    #premiere passe : creation de tous les auteurs
    entreprises = {}
    categories= {}
    for b in offres:
        a = b["entreprise"]
        if a not in entreprises:
            o = Entreprise(name=a, img=b["img"])
            db.session.add(o)
            entreprises[a]=o
        c = b["categorie"]
        if c not in categories:
            p = Categorie(name=c)
            db.session.add(p)
            categories[c]=p
    db.session.commit()

    # deuxieme pass: creation de tous les livres
    for b in offres:
        a = entreprises[b["entreprise"]]
        c = categories[b["categorie"]]
        o = Offre(salary = b["price"],
                title = b["title"],
                contact=b["contact"],
                description=b["description"],
                dd =b["ddepot"],
                dl = b["dlimite"],
                entreprise_id = a.id,
                categorie_id = c.id)
        db.session.add(o)
    db.session.commit()


@app.cli.command()
@click.argument('company')
def newcompany(company):
    '''Adds a new company'''
    from .models import Entreprise
    companyCapitalize = company.capitalize()
    result = Entreprise.query.filter(Entreprise.name==companyCapitalize).all()
    if (len(result)==0):
        society = Entreprise(name=companyCapitalize)
        db.session.add(society)
        db.session.commit()
    else:
        print("Company already registered, please contact Administrator")


@app.cli.command()
@click.argument('company')
def deletecompany(company):
    '''Delete new company'''
    from .models import Entreprise
    companyCapitalize = company.capitalize()
    try:
        society = Entreprise.query.filter(Entreprise.name==companyCapitalize).one()
        db.session.delete(society)
        db.session.commit()
    except:
        print("Something wrong occurs, please contact Administrator")


@app.cli.command()
@click.argument('username')
@click.argument('password')
@click.argument('company')
def newuser(username, password, company):
    '''Adds a new user'''
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    corporate_customer = Entreprise.get_entrepriselist4User()
    userCorporateList = get_corporateList(company)
    if ((company not in corporate_customer) or (company in userCorporateList)):
        print("First register Company with administrator")
    else:
        u = User(username=username, password=m.hexdigest(), company=company)
        print("Done")
        db.session.add(u)
        db.session.commit()

@app.cli.command()
@click.argument('username')
@click.argument('password')
@click.argument('email')
def newcandidate(username, password, email):
    '''Adds a new candidate'''
    from .models import Candidate
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    c = Candidate(username=username, password=m.hexdigest(), email=email)
    print("Done")
    db.session.add(c)
    db.session.commit()


@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username, password):
    '''Update passwd'''
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User(username=username, password=m.hexdigest())
    db.session.commit()
