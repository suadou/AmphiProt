from distutils.log import error
from http.client import FORBIDDEN
from turtle import done
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, BooleanField, EmailField
from wtforms.validators import InputRequired, Length, Regexp, Optional
from wtforms.widgets import TextArea, ListWidget
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import random
import json
from flask_restful import Api, Resource, reqparse
from datetime import datetime
import requests
from Bio import PDB
import prody

abspath = os.path.abspath(os.getcwd())

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'PotatoPatato'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:PotatoPatato98*@127.0.0.1/dbwdatabase'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loging'


class LogingForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,
                                                                           max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             max=255)])
    rememberme = BooleanField('Do you want to be remembered?')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,
                                                                           max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             max=255)])
    email = EmailField('Email', validators=[InputRequired()])
    affiliation = StringField('Affiliation', validators=[InputRequired()])
    country = StringField('Country', validators=[InputRequired()])


class Index_post_form(FlaskForm):
    PDB_id = StringField('PDB id', validators=[Optional(), Length(min=4, max=4), Regexp(
        "[A-Za-z0-9]", message="PDB id can only contain letters and numbers")])
    UniProt_id = StringField('UniProt id', validators=[Optional(), Length(min=4, max=16), Regexp(
        "[A-Za-z0-9]", message="UniProt id can only contain letters and numbers")])
    sequence = TextAreaField('Sequence', validators=[
                             Optional(), Length(min=50, max=1000)])
    file = FileField()
    table = SelectField(
        'Table', choices=[('Eisenberg', 'Eisenberg'), ('Kyte&Doolittle', 'Kyte & Doolittle'), ('Chothia', 'Chothia'), ('Janin', 'Janin'), ('Tanford', 'Tanford'), ('vonHeijne-Blomberg', 'VonHeijne-Blomberg'), ('Wimley', 'Wimley'), ('Wolfenden', 'Wolfenden')])
    BLAST = BooleanField('BLAST')
    isoelectric = BooleanField('Isoelectric point')


Options_table = db.Table('Options_table',
                         db.Column('Analysis_id', db.Integer,
                                   db.ForeignKey("Analysis.id")),
                         db.Column('Options_id', db.Integer,
                                   db.ForeignKey("Options.id"))
                         )


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    country = db.Column(db.String(255))
    affiliation = db.Column(db.String(255))
    analysiss = db.relationship('Analysis', backref='user')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Analysis(db.Model):
    __tablename__ = 'Analysis'
    id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.DateTime)
    Error = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    #     query_id = db.Column(db.Integer, db.ForeignKey("Query.id"))
    filess = db.relationship('Files', backref='analysis')
    options = db.relationship(
        'Options', secondary=Options_table, backref='analysis')


class Files(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True)
    impout = db.Column(db.Boolean)
    path = db.Column(db.String(255))
    queryid = db.Column(db.Integer) # Fuera, estaría solamente linkeado a analysis
    analyss_id = db.Column(db.Integer, db.ForeignKey("Analysis.id"))


class Options(db.Model):
    __tablename__ = 'Options'
    id = db.Column(db.Integer, primary_key=True)
    alltypes = db.Column(db.String(255))
    description = db.Column(db.String(255))
    table = db.Column(db.String(255))


@app.route('/')
def index():
    form = Index_post_form()
    createAnalysisOptions()
    return render_template('index.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def index_post():
    form = Index_post_form()
    data = {}
    if form.PDB_id.data:
        data["PDB_id"] = form.PDB_id.data
    elif form.UniProt_id.data:
        data["UniProt_id"] = form.UniProt_id.data
    elif form.sequence.data:
        data["sequence"] = form.sequence.data
        if check_fasta_input(data["sequence"]) == False:
            flash("FASTA format not correct. Remeber it is mandatory a '>' header. Sequence must contain only amino acids letters.", "error")
            return render_template('index.html', form=form)
        else:
            data["sequence"] = check_fasta_input(data["sequence"])
            if len(data["sequence"][1]) < 50 or len(data["sequence"][1]) > 1000:
                flash("Sequence must contain 50 to 1000 amino acids", "error")
                return render_template('index.html', form=form)


    #elif form.file.data:
     #   if form.validate_on_submit():
      #      f = form.file.meta
       #     return f
        #    filename = secure_filename(f)
        #    f.save(os.path.join(
         #   app.instance_path, 'file', filename
         #    ))
       # alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
        #data['file']=[app.instance_path, 'file', filename]
        #return data['file']
           # for protein in parsedmulti(sequence):
            #    if alphabets.search(protein) is not None:
             #       data['file'].append(protein)
        #return data['file']


    else:
        return redirect(url_for('index'))
    data["table"] = form.table.data
    data["BLAST"] = form.BLAST.data
    data["isoelectric"] = form.isoelectric.data
    if form.validate_on_submit():
        if current_user.is_anonymous:
            data["name"] = str(random.randint(1e9, 1e10))
            path = "static/data/"+data["name"]
            os.mkdir(path)
            with open("static/data/"+data["name"]+"/"+data["name"]+"_input.json", 'w') as fp:
                json.dump(data, fp)
                fp.close()
                return redirect(url_for('loading', out=data["name"]))
        else:
            #new_query = Query( Date = datetime.now(), Error = None)
            #try:
            #    db.session.add(new_query)
            #    db.session.commit()
            #except exc.IntegrityError:
             #   db.session.rollback()
             #   return render_template('loading.html', form=form)
            data["name"] = current_user.username
            new_analysis = Analysis(
                Date=datetime.now(), Error=None, user_id=current_user.get_id()) # añadir quieri_id = new_query.id
            try:
                db.session.add(new_analysis)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                return render_template('loading.html', form=form)
            #if data["BLAST"]:
             #   new_option = Options( alltypes = db.Column(db.String(255))
            with open("static/data/u_"+current_user.username+"/inputs/"+str(new_analysis.id)+"_input.json", 'w') as fp:
                json.dump(data, fp)
                fp.close()
            new_file = Files(impout=True, path="data/u_"+current_user.username+"/inputs/"
                             + str(new_analysis.id)+"_input.json",  analyss_id=new_analysis.id)
            try:
                db.session.add(new_file)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
                return render_template('loading.html', form=form)
            return redirect(url_for('loading', out=new_analysis.id))
    return render_template('index.html', form=form)

@app.route('/loading/<out>', methods=['GET', 'POST'])
def loading(out):
    if current_user.is_anonymous:
        f = open("static/data/"+out+"/"+out+"_input.json")
        data = json.load(f)
        print(data)
    else:
        f = open("static/data/u_"+current_user.username
                 + "/inputs/"+str(out)+"_input.json")
        data = json.load(f)
        data["name"] = "u_"+data["name"]+"/outputs"
    if data["table"]:
        table = read_table(data["table"])
    if "PDB_id" in data:
        analisis_ids = []
        analisis_ids.append(out)
        for id in data["PDB_id"]:
            if current_user.is_anonymous:
                chainsData = pdbstructdown(data["PDB_id"], out+"/"+out)
                with open("static/data/"+out+"/"+out+".json", 'w') as PDBjson:
                    json.dump(chainsData, PDBjson)
            else:
                chainsData = pdbstructdown(data["PDB_id"], "u_"+current_user.username+"/outputs/"+out+"_PDB")
                with open("static/data/u_"+current_user.username+"/outputs"+"/"+out+".json", 'w') as PDBjson:
                    json.dump(chainsData, PDBjson)
        for sequence in parsepdbgen(data["PDB_id"]):
            fourier(sequence[1], table, data["name"], out)
        if current_user.is_anonymous:
            return redirect(url_for('anonoutput', analysis_id=out))
        new_file = Files(impout=False, path="data/u_"+current_user.username
                            + "/outputs/"+str(out)+"_Fourier.png",  analyss_id=out)

        try:
            db.session.add(new_file)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        new_file = Files(impout=False, path="data/u_"+current_user.username
                     + "/outputs/"+str(out)+"_hydroplot.png",  analyss_id=out)

        try:
             db.session.add(new_file)
             db.session.commit()

        except exc.IntegrityError:
             db.session.rollback()

        f = open(f"static/data/u_"+current_user.username+"/outputs/"+out+".json")
        PDBdata = json.load(f)
        lastchain = len(PDBdata)
        new_file = Files(impout=False, path="data/u_"+current_user.username
                      + "/outputs/"+out+"_PDB_"+str(lastchain)+".pdb", analyss_id=out)
        try:
            db.session.add(new_file)
            db.session.commit()

        except exc.IntegrityError:
            db.session.rollback()

        #new_file = Files(impout=False, path="data/u_"+current_user.username
        #             + "/outputs/"+str(out)+"_PDBHit.pdb")
           #     new_analysis = Analysis(
           #     Date=datetime.now(), Error=None, user_id=current_user.get_id())
           #     try:
          #          db.session.add(new_analysis)
         #           db.session.commit()
             #   except exc.IntegrityError:
             #       db.session.rollback()
            #        out = new_analysis.id
            #        analisis_ids.append(out)
            #db.session.delete(out)
            #db.session.commiy()
        return redirect(url_for('output', analysis_id=out))
    elif "UniProt_id" in data:
        analisis_ids = []
        analisis_ids.append(out)
        for sequence in parseunicode(data["UniProt_id"]):
            fourier(sequence[1], table, data["name"], out)
            blast_record = prody.blastPDB(sequence[1])
            best_hit = blast_record.getBest()
            #with open("tempfile.json", 'w') as testjson:
            #    json.dump(best_hit, testjson)
            if current_user.is_anonymous:
                chainsData = pdbstructdown(best_hit['pdb_id'], out+"/"+out)
                with open("static/data/"+out+"/"+out+".json", 'w') as PDBjson:
                    json.dump(chainsData, PDBjson)
            else:
                chainsData = pdbstructdown(best_hit['pdb_id'], "u_"+current_user.username+"/outputs/"+out+"_PDB")
                with open("static/data/u_"+current_user.username+"/outputs"+"/"+out+".json", 'w') as PDBjson:
                    json.dump(chainsData, PDBjson)
        if current_user.is_anonymous:
            return redirect(url_for('anonoutput', analysis_id=out))
        new_file = Files(impout=False, path="data/u_"+current_user.username
                            + "/outputs/"+str(out)+"_Fourier.png",  analyss_id=out)

        try:
            db.session.add(new_file)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        new_file = Files(impout=False, path="data/u_"+current_user.username
                     + "/outputs/"+str(out)+"_hydroplot.png",  analyss_id=out)

        try:
             db.session.add(new_file)
             db.session.commit()

        except exc.IntegrityError:
             db.session.rollback()

        f = open(f"static/data/u_"+current_user.username+"/outputs/"+out+".json")
        PDBdata = json.load(f)
        lastchain = len(PDBdata)
        new_file = Files(impout=False, path="data/u_"+current_user.username
                      + "/outputs/"+out+"_PDB_"+str(lastchain)+".pdb", analyss_id=out)
        try:
            db.session.add(new_file)
            db.session.commit()

        except exc.IntegrityError:
            db.session.rollback()
           #     new_analysis = Analysis(
           #     Date=datetime.now(), Error=None, user_id=current_user.get_id())
           #     try:
          #          db.session.add(new_analysis)
         #           db.session.commit()
             #   except exc.IntegrityError:
             #       db.session.rollback()
            #        out = new_analysis.id
            #        analisis_ids.append(out)
            #db.session.delete(out)
            #db.session.commiy()
        if current_user.is_anonymous:
            return redirect(url_for('anonoutput', analysis_id=out))
        return redirect(url_for('output', analysis_id=out))
    elif "sequence" in data:
        fourier(data["sequence"][1], table, data["name"], out)
        blast_record = prody.blastPDB(data["sequence"][1])
        best_hit = blast_record.getBest()
        if current_user.is_anonymous:
            chainsData = pdbstructdown(best_hit['pdb_id'], out+"/"+out)
            with open("static/data/"+out+"/"+out+".json", 'w') as PDBjson:
                json.dump(chainsData, PDBjson)
        else:
            chainsData = pdbstructdown(best_hit['pdb_id'], "u_"+current_user.username+"/outputs/"+out+"_PDB")
            with open("static/data/u_"+current_user.username+"/outputs"+"/"+out+".json", 'w') as PDBjson:
                json.dump(chainsData, PDBjson)
        if not current_user.is_anonymous:
            new_file = Files(impout=False, path="data/u_"+current_user.username
                             + "/outputs/"+str(out)+"_Fourier.png",  analyss_id=out)

            try:
                db.session.add(new_file)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
            new_file = Files(impout=False, path="data/u_"+current_user.username
                             + "/outputs/"+str(out)+"_hydroplot.png",  analyss_id=out)

            try:
                db.session.add(new_file)
                db.session.commit()

            except exc.IntegrityError:
                db.session.rollback()

            f = open(f"static/data/u_"+current_user.username+"/outputs/"+out+".json")
            PDBdata = json.load(f)
            lastchain = len(PDBdata)
            new_file = Files(impout=False, path="data/u_"+current_user.username
                          + "/outputs/"+out+"_PDB_"+str(lastchain)+".pdb", analyss_id=out)
            try:
                db.session.add(new_file)
                db.session.commit()

            except exc.IntegrityError:
                db.session.rollback()
        
        if current_user.is_anonymous:
            return redirect(url_for('anonoutput', analysis_id=out))
        
        if "isoelectric" in data:
        	IP = isoelectric_p(data["sequence"][1], data["name"], out)
        	if not current_user.is_anonymous:
        	    new_file = Files(impout=False, path="data/u_"+current_user.username
        	                     + "/outputs/"+str(out)+"_isoelectric.txt",  analyss_id=out)
	
        	    try:
        	        db.session.add(new_file)
        	        db.session.commit()
        	    except exc.IntegrityError:
        	        db.session.rollback()
	
        	if current_user.is_anonymous:
        	    return redirect(url_for('anonoutput', analysis_id=out))
        return redirect(url_for('output', analysis_id=out))
    else:
        error

    return render_template('loading.html')


@app.route('/loging', methods=['GET', 'POST'])
def loging():
    form = LogingForm()
    if current_user.is_authenticated:
        flash("Already logged in, please logout.", "info")
        return redirect(url_for('index'))  # or whatever.
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.rememberme.data)
                flash("Logged in as " + user.username, "info")
                return redirect(url_for('workspace', user_id=current_user.username))
            flash("Invalid username or password", "error")
            return redirect(url_for('loging'))
    return render_template('loging.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        flash("Already logged in, please logout.", "info")
        return redirect(url_for('index'))
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        password=hashed, email=form.email.data,
                        country=form.country.data,
                        affiliation=form.affiliation.data)
        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            flash("Username/email already in use. Choose another one, please", "error")
            return render_template('register.html', form=form)
        finally:
            db.session.close()
        flash("You have successfully registered!", "info")
        userpath = abspath+"/static/data/"+f"u_{form.username.data}"
        try:
            os.mkdir(userpath)
            os.mkdir(userpath+"/outputs")
            os.mkdir(userpath+"/inputs")
        except OSError:
            flash("Something went very wrong. Start again please.", "error")
            return render_template('register.html', form=form)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/output/<analysis_id>')
def output(analysis_id):
    analysis = Analysis.query.filter_by(id=analysis_id).first()
    user = User.query.filter_by(username=current_user.username).first()
    if analysis.user_id != user.id:
        flash("You are not authorized here.", "error")
        return redirect(url_for('index'))
    f = open(f"static/data/u_"+current_user.username+"/outputs/"+analysis_id+".json")
    PDBdata = json.load(f)
    lastchainLen = PDBdata[-1][1]
    files = Files.query.filter_by(analyss_id=analysis_id)
    list = [str(files[1].path), str(files[2].path), str(files[3].path), lastchainLen]
    #list.append(data["PDB_id"]+".pdb")
    return render_template('output.html', list=list)


@app.route('/workspace/<user_id>')
@login_required
def workspace(user_id):
    user = User.query.filter_by(username=current_user.username).first()
    analysis = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.Date.desc())
    list = []
    for x in analysis:
        files = Files.query.filter_by(analyss_id=x.id)
        list += [files]
    return render_template('workspace.html', analysiss=analysis, list=list)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are now logged out", "info")
    return redirect(url_for('index'))

@app.route('/anonoutput/<analysis_id>')
def anonoutput(analysis_id):
    f = open(f"static/data/{analysis_id}/{analysis_id}.json")
    PDBdata = json.load(f)
    lastchain = len(PDBdata)
    lastchainLen = PDBdata[-1][1]
    #lastchainLen = PDBdata[str(len(PDBdata.keys()))][1]
    list = [f"data/{analysis_id}/{analysis_id}_Fourier.png",
            f"/data/{analysis_id}/{analysis_id}_hydroplot.png",
            f"data/{analysis_id}/{analysis_id}_{lastchain}.pdb",
            f"./data/{analysis_id}/{analysis_id}_isoelectric.txt",
            #f"data/{analysis_id}/{analysis_id}.json",
            lastchainLen]
    return render_template('anonoutput.html', list=list)
########## Functions ##########################################################

def check_fasta_input(input):
    import re
    seq = ""
    header = False
    for line in input.split("\n"):
        if header:
            seq += line.strip('\r')
        if '>' in line and header == False:
            id = line[1:].strip('\r')
            header = True
        if header == False:
            return False
    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
    if alphabets.search(seq) is not None:
        return (id, seq)
    else:
        return False


def read_table(table_name):
    table = {}
    fd = open("./tables/"+table_name, 'r')
    for line in fd:
        line = line.strip()
        (key, val) = line.split(" ")
        table[key] = val
    return table


def fourier(sequence, table, user, analysis):
    from matplotlib import pyplot, transforms
    from numpy import convolve, fft, mean, matrix, square
    hydro = [float(table.setdefault(aa.upper(), 0)) for aa in list(sequence)]
    km = [1/25] * 25
    Mean = convolve(hydro, km, 'same')
    y = 12
    b = -12
    S = []
    D = []
    ZERO = [0] * 25
    D = [ZERO] * 13
    while y <= (len(hydro)-(12)-1):
        while b <= 12:
            S.append((hydro[y+b]-Mean[y]))
            b += 1
        T = fft.fft(S)
        D.append(T)
        S = []
        b = -12
        y += 1
    Dn = D/mean(D)
    I = matrix(abs(Dn))
    I = square(I)
    pyplot.figure(figsize=(3, 7))
    pyplot.contourf(I[0:len(hydro)+12, 0:12])
    pyplot.xticks([25/3.6, 11], ["1/3.6", "1/2"])
    pyplot.grid(color='w', linestyle='-', linewidth=0.75)
    pyplot.savefig("./static/data/"+user+"/"+analysis+"_Fourier.png", transparent=True)
    pyplot.figure(figsize=(3, 7))
    km = [1/15] * 15
    base = pyplot.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)
    pyplot.plot(convolve(hydro, km, 'same'), 'r', transform=rot + base)
    pyplot.grid(color='b', linestyle='-', linewidth=0.75)
    pyplot.ylim([1, len(I)])
    pyplot.savefig("./static/data/"+user+"/"+analysis+"_hydroplot.png", transparent=True)


def unidown(code):
    url = "https://www.uniprot.org/uniprot/" + code + ".fasta"
    r = requests.get(url, allow_redirects=True).content.decode("utf-8")
    return r


def pdbdown(code):
    url = "https://www.rcsb.org/fasta/entry/" + code + "/download"
    r = requests.get(url, allow_redirects=True).content.decode("utf-8")
    return r

def pdbstructdown(code, out):
    url = "https://files.rcsb.org/download/" + code.upper() + ".pdb"
    r = requests.get(url, allow_redirects=True).content.decode("utf-8")
    PDBfile = open("static/data/"+out+".pdb", 'wt')
    for line in r:
        PDBfile.write(line)
    PDBfile.close()
    parser=PDB.PDBParser()
    io=PDB.PDBIO()
    structure = parser.get_structure(out, "static/data/"+out+".pdb")
    chainnum = 0
    chainsData = []
    for chain in structure.get_chains():
        chainnum += 1
        io.set_structure(chain)
        io.save("static/data/"+out+"_"+str(chainnum)+".pdb")

        with open("static/data/"+out+"_"+str(chainnum)+".pdb", 'r') as currentChain:
            chainLen = 0
            for line in currentChain:
                line_elements = line.split()
                if line_elements[0]=="ATOM" and line_elements[2] == "CA":
                    chainLen += 1
                    chainID = line_elements[4]
            chainsData.append([chainID, chainLen])

    return chainsData

def parsepdbgen(code):
    actual_protein = None
    sequence = ""
    string = pdbdown(code)
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                line = line.split("|")
                actual_protein = line[0].lstrip(">")
                continue
            yield tuple([actual_protein, sequence])
            line = line.split("|")
            actual_protein = line[0].lstrip(">")
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])


def parseunicode(code):
    actual_protein = None
    sequence = ""
    string = unidown(code)
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                line = line.split("|")
                actual_protein = line[1]
                continue
            yield tuple([actual_protein, sequence])
            line = line.split("|")
            actual_protein = line[1]
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])


def parsedmulti(string):
    actual_protein = None
    sequence = ""
    for line in string.split("\n"):
        if line.startswith(">"):
            if actual_protein is None:
                actual_protein = line
                continue
            yield tuple([actual_protein, sequence])
            actual_protein = line
            sequence = ""
            continue
        sequence += line
    yield tuple([actual_protein, sequence])

def createAnalysisOptions():
    All_Options = ["Hydrophobicity&Amphipatic", "IsoelectricPoint", "BLASTP", "Hydrophobicity&Amphipatic&IsoelectricPoint",
    "Hydrophobicity&Amphipatic&BLASTP", "Hydrophobicity&Amphipatic&IsoelectricPoint&BLASTP"]

    tables = ["Chothia", "Janin", "Tanford", "Wimley", "Eisenberg", "Kyte & Doolittle", "von Heijne-Blomberg", "Wolfenden"]

    for eachOption in All_Options:
        for eachTable in tables:
            new_option = Options(
            alltypes = eachOption,
            description = "Compute" + eachOption,
            table = eachTable,
            )
            try:
                db.session.add(new_option)
                db.session.commit()
            except:
                db.session.rollback()
            finally:
                db.session.close()

def isoelectric_p(sequence, user, analysis):
    from isoelectric import ipc
    isoelectric_point = ipc.predict_isoelectric_point_ProMoST(sequence)
    with open("./static/data/"+user+"/"+analysis+"_isoelectric.txt", 'w') as f:
        f.write('%f' % isoelectric_point)
                
# I left this at the end bc I am not sure if it has to be there?
if __name__ == '__main__':
    app.run(debug=True)
