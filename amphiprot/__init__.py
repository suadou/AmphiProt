from distutils.log import error
from http.client import FORBIDDEN
from turtle import done
from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
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
from werkzeug.utils import secure_filename
import re
from Bio import PDB
import prody
import requests
from isoelectric import ipc
from matplotlib import pyplot, transforms
from numpy import convolve, fft, mean, matrix, square, savetxt

def create_app(test_config=None):
    abspath = os.path.abspath(os.getcwd())

    app = Flask(__name__)
    api = Api(app)
    app.config['SECRET_KEY'] = 'PotatoPatato'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1942_wad@127.0.0.1/dbwdatabase'
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
                                Optional(), Length(min=50, max=1000000)])
        file_input = FileField()
        table = SelectField(
            'Table', choices=[('Eisenberg', 'Eisenberg'), ('Kyte&Doolittle', 'Kyte & Doolittle'), ('Chothia', 'Chothia'), ('Janin', 'Janin'), ('Tanford', 'Tanford'), ('VonHeijen-Blomberg', 'VonHeijen-Blomberg'), ('Wimley', 'Wimley'), ('Wolfenden', 'Wolfenden')])
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

    class Query(db.Model):
        __tablename__ = 'Query'
        id = db.Column(db.Integer, primary_key=True)
        Date = db.Column(db.DateTime)
        Error = db.Column(db.String(255))
        analysiss = db.relationship('Analysis', backref='Query')


    class Analysis(db.Model):
        __tablename__ = 'Analysis'
        id = db.Column(db.Integer, primary_key=True)
        Date = db.Column(db.DateTime)
        Error = db.Column(db.String(255))
        protein_name = db.Column(db.String(255))
        user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
        query_id = db.Column(db.Integer, db.ForeignKey("Query.id"))
        filess = db.relationship('Files', backref='Analysis')
        options = db.relationship(
            'Options', secondary=Options_table, backref='Analysis')


    class Files(db.Model):
        __tablename__ = 'Files'
        id = db.Column(db.Integer, primary_key=True)
        input = db.Column(db.Boolean)
        path = db.Column(db.String(255))
        analyss_id = db.Column(db.Integer, db.ForeignKey("Analysis.id"))


    class Options(db.Model):
        __tablename__ = 'Options'
        id = db.Column(db.Integer, primary_key=True)
        alltypes = db.Column(db.String(255))
        description = db.Column(db.String(255))
        table = db.Column(db.String(255))


    @app.route('/amphiprot/')
    def index():
        form = Index_post_form()
        #createAnalysisOptions()
        return render_template('index.html', form=form)


    @app.route('/amphiprot/', methods=['GET', 'POST'])
    def index_post():
        form = Index_post_form()
        data = {}
        raw_data = {}
        if form.PDB_id.data:
            data["PDB_id"] = form.PDB_id.data
        elif form.UniProt_id.data:
            data["UniProt_id"] = form.UniProt_id.data
        elif form.sequence.data:
            raw_data["query"] = form.sequence.data
        elif form.file_input.data:
            data['file'] = form.file_input.data
        else:
            return redirect(url_for('index'))
        data["table"] = form.table.data
        data["BLAST"] = True
        data["isoelectric"] = form.isoelectric.data
        options_descriptor = 'Hydrophobicity&Amphipatic'
        if (data["isoelectric"] == True):
            options_descriptor = options_descriptor + '&IsoelectricPoint'
        if (data["BLAST"] == True ):
            options_descriptor = options_descriptor + '&BLASTP'
        if form.validate_on_submit():
            if current_user.is_anonymous:
                i = 1
                data["name"] = str(random.randint(1e9, 1e10))
                data["date"] = str(datetime.now())
                path = app.root_path + "/static/data/"+data["name"]
                os.mkdir(path)
                if "PDB_id" in data:
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    for sequence in parsepdbgen(data["PDB_id"]):
                        if sequence[0] == None:
                            flash('PDB id ' + data['PDB_id'] + ' does not exist', 'error')
                            return redirect(url_for('index'))
                           
                        elif alphabets.search(sequence[1]) is not None:
                            data['protein_name'] = sequence[0]
                            data['sequence'] = sequence[1]
                            with open(path + '/' + str(i) + '_input.json', 'w') as fp:
                                json.dump(data, fp)
                                fp.close()
                            i += 1
                        else:
                            flash('PDB id ' + data['PDB_id'] + ' does not exist', 'error')
                elif "UniProt_id" in data:
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    for sequence in parseunicode(data["UniProt_id"]):
                        if sequence[0] == None:
                            flash('UniProt id ' + data['UniProt_id'] + ' does not exist', 'error')
                            return redirect(url_for('index'))
                        if alphabets.search(sequence[1]) is not None:
                            data['protein_name'] = sequence[0]
                            data['sequence'] = sequence[1]
                            with open(path + '/' + str(i) + '_input.json', 'w') as fp:
                                json.dump(data, fp)
                                fp.close()
                            i += 1
                        else:
                            flash('UniProt id ' + data['UniProt_id'] + ' does not exist', 'error')
                elif "query" in raw_data:
                    if raw_data["query"].startswith(">"):
                        alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                        for sequence in parsedmulti(raw_data["query"]):
                            if sequence[0] == None:
                                flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                                return redirect(url_for('index'))
                            elif alphabets.search(sequence[1]) is not None:
                                data['protein_name'] = sequence[0]
                                data['sequence'] = sequence[1]
                                with open(path + '/' + str(i) + '_input.json', 'w') as fp:
                                    json.dump(data, fp)
                                    fp.close()
                                i += 1
                            else:
                                flash('Invalid format in sequence ' + sequence[0], 'error')
                                return redirect(url_for('index'))
                    else:
                        flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                        return redirect(url_for('index'))
                elif "file" in data:
                    del data["file"]
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    filename = secure_filename(form.file_input.data.filename)
                    form.file_input.data.save(app.root_path + '/static/tmp/'+filename)
                    ff = open(app.root_path + '/static/tmp/'+filename, 'r')
                    raw_data["file"] = ff.read()
                    ff.close()
                    os.remove(app.root_path + '/static/tmp/'+filename)
                    if raw_data["file"].startswith(">"):
                        for sequence in parsedmulti(raw_data["file"]):
                            if sequence[0] == None:
                                flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                                return redirect(url_for('index'))
                            elif alphabets.search(sequence[1]) is not None:
                                data['protein_name'] = sequence[0]
                                data['sequence'] = sequence[1]
                                with open(path + '/' + str(i) + '_input.json', 'w') as fp:
                                    json.dump(data, fp)
                                    fp.close()
                                i += 1
                            else:
                                flash('Invalid format in sequence ' + sequence[0], 'error')
                                return redirect(url_for('index'))
                    else:
                        flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                        return redirect(url_for('index'))
                return redirect(url_for('loading', out=data['name']))
            else:
                new_query = Query( Date = datetime.now(), Error = None)
                try:
                    db.session.add(new_query)
                    db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
                data["name"] = current_user.username
                new_options = Options.query.filter_by(alltypes=options_descriptor, table=data['table']).first()
                if "PDB_id" in data:
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    for sequence in parsepdbgen(data["PDB_id"]):
                        if alphabets.search(sequence[1]) is not None:
                            data['protein_name'] = sequence[0]
                            data['sequence'] = sequence[1]
                            new_analysis = Analysis(
                                Date=datetime.now(), Error=None, protein_name = sequence[0], user_id=current_user.get_id(), query_id = new_query.id)
                            new_analysis.options.append(new_options)
                            try:
                                db.session.add(new_analysis)
                                db.session.commit()
                            except exc.IntegrityError:
                                db.session.rollback()
                            with open(app.root_path + "/static/data/u_"+current_user.username+"/inputs/"+str(new_analysis.id)+"_input.json", 'w') as fp:
                                json.dump(data, fp)
                                fp.close()
                            new_file = Files(input=True, path="data/u_"+current_user.username+"/inputs/"
                                    + str(new_analysis.id)+"_input.json",  analyss_id=new_analysis.id)
                            try:
                                db.session.add(new_file)
                                db.session.commit()
                            except exc.IntegrityError:
                                db.session.rollback()
                        else:
                            flash('PDB id ' + data['PDB_id'] + ' does not exist', 'error')
                elif "UniProt_id" in data:
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    for sequence in parseunicode(data["UniProt_id"]):
                        if alphabets.search(sequence[1]) is not None:
                            data['protein_name'] = sequence[0]
                            data['sequence'] = sequence[1]
                            new_analysis = Analysis(
                                Date=datetime.now(), Error=None, user_id=current_user.get_id(), query_id = new_query.id, protein_name = sequence[0])
                            new_analysis.options.append(new_options)
                            try:
                                db.session.add(new_analysis)
                                db.session.commit()
                            except exc.IntegrityError:
                                db.session.rollback()
                            with open(app.root_path +"/static/data/u_"+current_user.username+"/inputs/"+str(new_analysis.id)+"_input.json", 'w') as fp:
                                json.dump(data, fp)
                                fp.close()
                            new_file = Files(input=True, path="data/u_"+current_user.username+"/inputs/"
                                    + str(new_analysis.id)+"_input.json",  analyss_id=new_analysis.id)
                            try:
                                db.session.add(new_file)
                                db.session.commit()
                            except exc.IntegrityError:
                                db.session.rollback()
                        else:
                            flash('UniProt id ' + data['UniProt_id'] + ' does not exist', 'error')
                elif "query" in raw_data:
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    if raw_data["query"].startswith(">"):
                        for sequence in parsedmulti(raw_data["query"]):
                            if sequence[0] == None:
                                flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                                return redirect(url_for('index'))
                            elif alphabets.search(sequence[1]) is not None:
                                data['protein_name'] = sequence[0]
                                data['sequence'] = sequence[1]
                                new_analysis = Analysis(
                                Date=datetime.now(), Error=None, user_id=current_user.get_id(), query_id = new_query.id, protein_name = sequence[0])
                                new_analysis.options.append(new_options)
                                try:
                                    db.session.add(new_analysis)
                                    db.session.commit()
                                except exc.IntegrityError:
                                    db.session.rollback()
                                with open(app.root_path + "/static/data/u_"+current_user.username+"/inputs/"+str(new_analysis.id)+"_input.json", 'w') as fp:
                                    json.dump(data, fp)
                                    fp.close()
                                new_file = Files(input=True, path="data/u_"+current_user.username+"/inputs/"+ str(new_analysis.id)+"_input.json",  analyss_id=new_analysis.id)
                                try:
                                    db.session.add(new_file)
                                    db.session.commit()
                                except exc.IntegrityError:
                                    db.session.rollback()
                            else:
                                flash('Invalid format in sequence ' + sequence[0], 'error')
                                return redirect(url_for('index'))
                    else:
                        flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                        return redirect(url_for('index'))
                elif "file" in data:
                    del data["file"]
                    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
                    filename = secure_filename(form.file_input.data.filename)
                    form.file_input.data.save(app.root_path + '/static/tmp/'+filename)
                    ff = open(app.root_path + '/static/tmp/'+filename, 'r')
                    raw_data["file"] = ff.read()
                    ff.close()
                    os.remove(app.root_path + '/static/tmp/'+filename)
                    if raw_data["file"].startswith(">"):
                        for sequence in parsedmulti(raw_data["file"]):
                            if sequence[0] == None:
                                flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                                return redirect(url_for('index'))
                            elif alphabets.search(sequence[1]) is not None:
                                data['protein_name'] = sequence[0]
                                data['sequence'] = sequence[1]
                                new_analysis = Analysis(
                                Date=datetime.now(), Error=None, user_id=current_user.get_id(), query_id = new_query.id, protein_name = sequence[0])
                                new_analysis.options.append(new_options)
                                try:
                                    db.session.add(new_analysis)
                                    db.session.commit()
                                except exc.IntegrityError:
                                    db.session.rollback()
                                with open(app.root_path + "/static/data/u_"+current_user.username+"/inputs/"+str(new_analysis.id)+"_input.json", 'w') as fp:
                                    json.dump(data, fp)
                                    fp.close()
                                new_file = Files(input=True, path="data/u_"+current_user.username+"/inputs/"+ str(new_analysis.id)+"_input.json",  analyss_id=new_analysis.id)
                                try:
                                    db.session.add(new_file)
                                    db.session.commit()
                                except exc.IntegrityError:
                                    db.session.rollback()
                            else:
                                flash('Invalid format in sequence' + sequence[0], 'error')
                                return redirect(url_for('index'))
                    else:
                        flash('Invalid format. Remember it is necessary to include a FASTA header.', 'error')
                        return redirect(url_for('index'))
                return redirect(url_for('loading', out=new_query.id))
        return render_template('index.html', form=form)

    @app.route('/amphiprot/loading/<out>', methods=['GET', 'POST'])
    def loading(out):
        if current_user.is_anonymous:
            file_num = 0
            files = os.listdir(app.root_path + "/static/data/"+out)
            for file in files:
                if re.compile('_input.json$').search(file) is not None:
                    file_num += 1
                    actual_file = file.rstrip('_input.json')
                    f = open(app.root_path + "/static/data/"+out+"/"+file)
                    data = json.load(f)
                    table = read_table(data['table'])
                    fourier(data['sequence'], table, out, file.strip('_input.json'))
                    if data["isoelectric"]:
                        isoelectric_p(data["sequence"], out, file.strip('_input.json')) # revisarlo, no se si funciona
                    if 'PDB_id' in data.keys():
                        pdbstructdown(data['PDB_id'], out+"/"+file.strip('_input.json')+"_PDB", file_num)
                        with open("tempfile.json", 'w') as testjson:
                            testjson.write(out+"/"+file.strip('_input.json')+"_PDB")
                    else:
                        blast_record = prody.blastPDB(data['sequence'], timeout=9999)
                        try:
                            best_hit = blast_record.getBest()
                            pdbstructdown(best_hit['pdb_id'], out+"/"+file.strip('_input.json')+"_PDB", best_hit['chain_id'])
                        except TypeError as e:
                            pass
            if file_num > 1:
                return redirect(url_for('anonworkspace', anonuser_id=out))
            elif file_num == 1:
                return redirect(url_for('anonoutput', anonuser_id=out, analysis_id=actual_file))

        else:
            analysis_num = 0
            for analysis in Analysis.query.filter_by(query_id = out).all():
                analysis_num = analysis_num + 1
                f = open(app.root_path + "/static/data/"+ "u_"+ current_user.username+"/inputs/"+str(analysis.id)+"_input.json")
                data = json.load(f)
                table = read_table(data['table'])
                fourier(data['sequence'], table, "u_"+ current_user.username+"/outputs" , str(analysis.id))
                if data["isoelectric"]:
                    isoelectric_p(data['sequence'], "u_"+ current_user.username+"/outputs" , str(analysis.id))
                    files_sufix = ["_Fourier.png", "_hydroplot.png", "_fourier.out", "_hydro.out", "_isoelectric.out"]
                else:
                    files_sufix = ["_Fourier.png", "_hydroplot.png", "_fourier.out", "_hydro.out"]
                for sufix in files_sufix:
                    new_file = Files(input=False, path="data/u_"+current_user.username+"/outputs/"
                                + str(analysis.id)+sufix,  analyss_id=analysis.id)
                    try:
                        db.session.add(new_file)
                        db.session.commit()
                    except exc.IntegrityError:
                        db.session.rollback()
                if 'PDB_id' in data.keys():
                    pdbstructdown(data['PDB_id'], "u_"+current_user.username+"/outputs/"+str(analysis.id)+"_PDB", analysis_num)
                    new_file = Files(input=False, path="data/u_"+current_user.username+"/outputs/"
                            +str(analysis.id)+"_PDB.pdb", analyss_id=analysis.id)
                else:
                    blast_record = prody.blastPDB(data['sequence'], timeout=9999)
                    try:
                        best_hit = blast_record.getBest()
                        pdbstructdown(best_hit['pdb_id'], "u_"+current_user.username+"/outputs/"+str(analysis.id)+"_PDB", best_hit['chain_id'])
                        new_file = Files(input=False, path="/data/u_"+current_user.username+"/outputs/"
                                +str(analysis.id)+"_PDB.pdb", analyss_id=analysis.id)
                    except TypeError as e:
                        pass
                try:
                    db.session.add(new_file)
                    db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
            if analysis_num > 1:
                return redirect(url_for('workspace', user_id=current_user.get_id()))
            elif analysis_num == 1:
                return redirect(url_for('output', analysis_id=analysis.id))
        return render_template('loading.html')


    @app.route('/amphiprot/loging', methods=['GET', 'POST'])
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


    @app.route('/amphiprot/register', methods=['GET', 'POST'])
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
            userpath = app.root_path +"/static/data/"+f"u_{form.username.data}"
            try:
                os.mkdir(userpath)
                os.mkdir(userpath+"/outputs")
                os.mkdir(userpath+"/inputs")
            except OSError:
                flash("Something went very wrong. Start again please.", "error")
                return render_template('register.html', form=form)
            return redirect(url_for('index'))
        return render_template('register.html', form=form)


    @app.route('/amphiprot/help')
    def help():
        return render_template('help.html')


    @app.route('/amphiprot/output/<analysis_id>')
    def output(analysis_id):
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        user = User.query.filter_by(username=current_user.username).first()
        if analysis.user_id != user.id:
            flash("You are not authorized here.", "error")
            return redirect(url_for('index'))
        chainLen = 0
        if os.path.exists(app.root_path + "/static/data/u_"+current_user.username+"/outputs/"+analysis_id+"_"+"PDB.pdb"):
            with open(app.root_path + "/static/data/u_"+current_user.username+"/outputs/"+analysis_id+"_"+"PDB.pdb", 'r') as currentChain:
                for line in currentChain:
                    line_elements = line.split()
                    if line_elements[0]=="ATOM" and line_elements[2] == "CA":
                        chainLen += 1
        else:
            flash("PDB Download for this output failed. Structure visualization will not work")
        files = Files.query.filter_by(analyss_id=analysis_id)
        list = [str(files[1].path), str(files[2].path), str(files[-1].path), chainLen,str(files[3].path),str(files[4].path)]
        #list.append(data["PDB_id"]+".pdb")
        if os.path.isfile(app.root_path + "/static/data/u_"+current_user.username+"/outputs/"+analysis_id+"_"+"isoelectric.out"):
            with open(app.root_path + "/static/data/u_"+current_user.username+"/outputs/"+analysis_id+"_"+"isoelectric.out", 'r') as f:
                content = f.read()
                return render_template('output.html', list=list, content=content)
        else:
            return render_template('output.html', list=list)


    @app.route('/amphiprot/workspace/<user_id>')
    @login_required
    def workspace(user_id):
        user = User.query.filter_by(username=current_user.username).first()
        analysis = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.Date.desc())
        list = []
        for x in analysis:
            files = Files.query.filter_by(analyss_id=x.id)
            list += [files]
        return render_template('workspace.html', analysiss=analysis, list=list)

    @app.route('/amphiprot/download/<analysis_id>', methods=['GET', 'POST'])
    @login_required
    def download(analysis_id):
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        user = User.query.filter_by(username=current_user.username).first()
        if analysis.user_id != user.id:
            flash("You are not authorized here.", "error")
            return redirect(url_for('index'))
        files = Files.query.filter_by(analyss_id=analysis_id)
        file = str(files[0].path)
        path = file.split("/")
        return send_from_directory(directory=app.root_path +"/static/"+ "/".join(path[0:-1]), path=app.root_path +"/static/"+ "/".join(path[0:-1]), filename=path[-1], as_attachment=True)
        
    @app.route('/amphiprot/download/anonoutput/<anonuser_id>/<analysis_id>', methods=['GET', 'POST'])
    def anondownload(anonuser_id, analysis_id):
        return send_from_directory(directory = app.root_path +"/static/data/"+ anonuser_id , path = app.root_path +"/static/data/"+ anonuser_id , filename= analysis_id + "_input.json" , as_attachment=True)

    @app.route('/amphiprot/logout')
    @login_required
    def logout():
        logout_user()
        flash("You are now logged out", "info")
        return redirect(url_for('index'))

    @app.route('/amphiprot/anonoutput/<anonuser_id>/<analysis_id>')
    def anonoutput(anonuser_id, analysis_id):
        f = open(f"{app.root_path}/static/data/{anonuser_id}/{analysis_id}_input.json")
        if os.path.exists(f"{app.root_path}/static/data/{anonuser_id}/{analysis_id}_PDB.pdb"):
            with open(f"{app.root_path}/static/data/{anonuser_id}/{analysis_id}_PDB.pdb", 'r') as currentChain:
                chainLen = 0
                for line in currentChain:
                    line_elements = line.split()
                    if line_elements[0]=="ATOM" and line_elements[2] == "CA":
                        chainLen += 1
        else:
            flash("PDB Download for this output failed. Structure visualization will not work")
        
        if os.path.isfile(f"{app.root_path}/static/data/{anonuser_id}/{analysis_id}_isoelectric.out"):
            list = [f"data/{anonuser_id}/{analysis_id}_Fourier.png",
                f"data/{anonuser_id}/{analysis_id}_hydroplot.png",
                f"data/{anonuser_id}/{analysis_id}_PDB.pdb",
                chainLen,
            f"data/{anonuser_id}/{analysis_id}_fourier.out",
            f"data/{anonuser_id}/{analysis_id}_hydro.out",
            f"data/{anonuser_id}/{analysis_id}_isoelectric.out"]
            with open(f"{app.root_path}/static/data/{anonuser_id}/{analysis_id}_isoelectric.out", 'r') as f:
                content = f.read()
                return render_template('anonoutput.html', list=list, content=content)
        else:
            list = [f"data/{anonuser_id}/{analysis_id}_Fourier.png",
                f"/data/{anonuser_id}/{analysis_id}_hydroplot.png",
                f"data/{anonuser_id}/{analysis_id}_PDB.pdb",
                chainLen,
            f"data/{anonuser_id}/{analysis_id}_fourier.out",
            f"data/{anonuser_id}/{analysis_id}_hydro.out"]
            return render_template('anonoutput.html', list=list)
        

    @app.route('/amphiprot/anonworkspace/<anonuser_id>')
    def anonworkspace(anonuser_id):
        analysis = {}
        try:
            files = os.listdir(f"{app.root_path}/static/data/{anonuser_id}")
            for file in files:
                if re.compile('_input.json$').search(file) is not None:
                    f = open(app.root_path +"/static/data/" + anonuser_id + "/" + file)
                    data = json.load(f)
                    analysis[file.rstrip('_input.json')] = {'protein_name' : data['protein_name'], 'date' : data['date'], 'id' : file.rstrip('_input.json')}
            return render_template('anonworkspace.html', analysiss=analysis, user = anonuser_id)
        except FileNotFoundError:
            flash('File not found.', 'error')
            return redirect(url_for('index'))
            
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
        fd = open(app.root_path + "/tables/"+table_name, 'r')
        for line in fd:
            line = line.strip()
            (key, val) = line.split(" ")
            table[key] = val
        return table


    def fourier(sequence, table, user, analysis):
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
        pyplot.savefig(app.root_path + "/static/data/"+user+"/"+analysis+"_Fourier.png", transparent=True)
        pyplot.figure(figsize=(3, 7))
        km = [1/15] * 15
        base = pyplot.gca().transData
        rot = transforms.Affine2D().rotate_deg(90)
        pyplot.plot(convolve(hydro, km, 'same'), 'r', transform=rot + base)
        pyplot.grid(color='b', linestyle='-', linewidth=0.75)
        pyplot.ylim([1, len(I)])
        pyplot.savefig(app.root_path + "/static/data/"+user+"/"+analysis+"_hydroplot.png", transparent=True)
        savetxt(app.root_path +  "/static/data/"+user+"/"+analysis+"_fourier.out", I[0:len(hydro)+12, 0:12], delimiter=",")
        fp = open(app.root_path +  "/static/data/"+user+"/"+analysis+"_hydro.out", 'w')
        for line in hydro:
            fp.write(str(line)+'\n')
        fp.close()



    def unidown(code):
        url = "https://www.uniprot.org/uniprot/" + code + ".fasta"
        r = requests.get(url, allow_redirects=True).content.decode("utf-8")
        return r


    def pdbdown(code):
        url = "https://www.rcsb.org/fasta/entry/" + code + "/download"
        r = requests.get(url, allow_redirects=True).content.decode("utf-8")
        return r

    def pdbstructdown(code, out, input_chainnum):
        url = "https://files.rcsb.org/download/" + code.upper() + ".pdb"
        r = requests.get(url, allow_redirects=True).content.decode("utf-8")
        PDBfile = open(app.root_path + "/static/data/tempPDB.pdb", 'wt')
        for line in r:
            PDBfile.write(line)
        PDBfile.close()
        parser=PDB.PDBParser()
        io=PDB.PDBIO()
        structure = parser.get_structure(out,app.root_path + "/static/data/tempPDB.pdb")
        chainnum = 0
        chainsData = []
        for chain in structure.get_chains():
            chainnum += 1
            if chainnum == input_chainnum or chain.get_id() == input_chainnum:
                io.set_structure(chain)
                io.save(app.root_path + "/static/data/"+out+".pdb")
        os.remove(app.root_path + "/static/data/tempPDB.pdb")

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
            sequence += line.rstrip("\n")
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
            sequence += line.rstrip("\n")
        yield tuple([actual_protein, sequence])


    def parsedmulti(string):
        #string = string.replace('\r', '')
        actual_protein = None
        sequence = ""
        for line in string.splitlines():
            if line.startswith(">"):
                if actual_protein is None:
                    line = line.split("|")
                    try:
                        actual_protein = line[1]
                    except:
                        actual_protein = line[0][1:]
                    continue
                yield tuple([actual_protein, sequence])
                line = line.split("|")
                try:
                    actual_protein = line[1]
                except:
                    actual_protein = line[0][1:]
                sequence = ""
                continue
            sequence += line.rstrip("\n")
        yield tuple([actual_protein, sequence])

    def createAnalysisOptions():
        All_Options = ["Hydrophobicity&Amphipatic", "IsoelectricPoint", "BLASTP", "Hydrophobicity&Amphipatic&IsoelectricPoint",
        "Hydrophobicity&Amphipatic&BLASTP", "Hydrophobicity&Amphipatic&IsoelectricPoint&BLASTP"]

        tables = ["Chothia", "Janin", "Tanford", "Wimley", "Eisenberg", "Kyte&Doolittle", "vonHeijne-Blomberg", "Wolfenden"]

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
        isoelectric_point = ipc.predict_isoelectric_point_ProMoST(sequence.upper())
        with open(app.root_path + "/static/data/"+user+"/"+analysis+"_isoelectric.out", 'w') as f:
            f.write('%f' % isoelectric_point)

    return app
