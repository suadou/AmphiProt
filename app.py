from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, BooleanField
from wtforms.validators import InputRequired, Length, Regexp
from wtforms.widgets import TextArea, ListWidget
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import random
from flask_restful import Api, Resource, reqparse

abspath = os.path.abspath(os.getcwd())
file_path = abspath + "/database.db"

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'PotatoPatato'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loging'


class LogingForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,
                                                                           max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             max=80)])


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,
                                                                           max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,
                                                                             max=80)])


class Index_post_form(FlaskForm):
    PDB_id = StringField('PDB_id', validators=[
                                               Length(min=4, max=4), Regexp('[0-9A-Za-z]')])
    UniProt_id = StringField('UniProt_id', validators=[
                             Length(min=4, max=16), Regexp('[0-9A-Za-z]')])
    sequence = TextAreaField('Sequence', validators=[
                             Length(min=50)], widget=TextArea())
    file = FileField()
    table = SelectField(
        'Table', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    BLAST = BooleanField('BLAST')
    isoelectric = BooleanField('Isoelectric point')


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(80))
    analysiss = db.relationship('Analysis', backref='user')
    filess = db.relationship('Files', backref='user')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Analysis(db.Model):
    __tablename__ = 'Analysis'
    id = db.Column(db.Integer, primary_key=True)
    Ampreg = db.Column(db.Boolean)
    Hydro = db.Column(db.Boolean)
    Isopoint = db.Column(db.Boolean)
    Blastp = db.Column(db.Boolean)
    Date = db.Column(db.DateTime)
    Error = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    table_id = db.Column(db.Integer, db.ForeignKey("Table.id"))
    filess = db.relationship('Files', backref='analysis')


class Files(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True)
    impout = db.Column(db.Boolean)
    path = db.Column(db.String(80))
    queryid = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    analysis_id = db.Column(db.Integer, db.ForeignKey("Analysis.id"))


class Table(db.Model):
    __tablename__ = 'Table'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(80))
    typetable = db.Column(db.Integer)
    analysiss = db.relationship('Analysis', backref='table')


@app.route('/')
def index():
    form = Index_post_form()
    return render_template('index.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def index_post():
    form = Index_post_form()
    PDB_id = form.PDB_id.data
    UniProt_id = form.UniProt_id.data
    sequence = form.sequence.data
    table = form.table.data
    BLAST = form.BLAST.data
    isoelectric = form.isoelectric.data
    if form.validate_on_submit():
        if current_user.is_anonymous:
            name = str(random.randint(1e9, 1e10))
        else:
            name = current_user.username
    return render_template('index.html', form=form)


@app.route('/loging', methods=['GET', 'POST'])
def loging():
    form = LogingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=False)
                flash("Logged in as " + user.username, "info")
                return redirect(url_for('workspace', user_id=current_user.username))
            flash("Invalid username or password", "error")
            return redirect(url_for('loging'))
    return render_template('loging.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        password=hashed)
        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            flash("Username already exists. Choose another one, please", "error")
            return render_template('register.html', form=form)
        flash("You have successfully registered!", "info")
        userpath = abspath+"/data/"+f"u_{form.username.data}"
        os.mkdir(userpath)
        os.mkdir(userpath+"/outputs")
        os.mkdir(userpath+"/inputs")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/workspace/<user_id>')
@login_required
def workspace(user_id):
    return render_template('workspace.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



#### API stuff

names_put_args = reqparse.RequestParser()
names_put_args.add_argument("username", type=str, help="Please enter a valid username", required=True)
names_put_args.add_argument("password", type=str, help="Please enter a valid password", required=True)


names = {}

class NewUser(Resource):
    def put(self):
        args = names_put_args.parse_args()
        return args

api.add_resource(NewUser, "/api_register")

#@app.route('/api_register', methods=['POST'])
#def register():
    #form = RegistrationForm()
#    if form.validate_on_submit():
#        hashed = generate_password_hash(form.password.data, method='sha256')
#        new_user = User(username=form.username.data,
#                        password=hashed)
#        db.session.add(new_user)
#        db.session.commit()
#        flash("You have successfully registered!", "info")
#        return redirect(url_for('index'))
#    return render_template('register.html', form=form)
    #return jsonify({ 'username': new_user.username }), 201, {'Location': url_for('get_user', id = new_user.id, _external = True)}
    #return {"Status": "Successfully registered"}



# I left this at the end bc I am not sure if it has to be there?
if __name__ == '__main__':
    app.run(debug=True)
