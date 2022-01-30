from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os


file_path = os.path.abspath(os.getcwd())+"/database.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PotatoPatato'
# Falta
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


class User(UserMixin, db.Model):  # quizas hace falta unique id pa esto, tengo duda
    __tablename__ = 'User'
    username = db.Column(db.String(25), primary_key=True, unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(username):
    return User.query.get(str(username))


class Analysis(db.Model):
    __tablename__ = 'Analysis'
    id = db.Column(db.Integer, primary_key=True)
    Ampreg = db.Column(db.Boolean)
    Hydro = db.Column(db.Boolean)
    Isopoint = db.Column(db.Boolean)
    Blastp = db.Column(db.Boolean)
    Date = db.Column(db.DateTime)
    Error = db.Column(db.String(80))
    #user_id = db.Column(db.String(25), db.ForeignKey("User.username"))
    #table_id = db.Column(db.Integer, db.ForeignKey("Table.id"))
    #user = db.relationship("User", foreign_keys=[user_id])
    #table = db.relationship("Table", foreign_keys=[table_id])


class Files(db.Model):
    __tablename__ = 'Files'
    id = db.Column(db.Integer, primary_key=True)
    impout = db.Column(db.Boolean)
    path = db.Column(db.String(80))
    queryid = db.Column(db.Integer)
    #user_id = db.Column(db.String(25), db.ForeignKey("User.username"))
    #analysis_id = db.Column(db.Integer, db.ForeignKey("Analysis.id"))
    #user = db.relationship("User", foreign_keys=[user_id])
    #analysis = db.relationship("Table", foreign_keys=[analysis_id])


class Table(db.Model):
    __tablename__ = 'Table'
    id = db.Column(db.Integer, primary_key=True)
    typetable = db.Column(db.Integer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loging', methods=['GET', 'POST'])
def loging():
    form = LogingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                #login_user(user, remember=True)
                #return redirect(url_for('workspace'))
                return '<h1>Works okey</h1>'
            return '<h1>Invalid username or password</h1>'
    return render_template('loging.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>Works yey</h1>'
    return render_template('register.html', form=form)


@app.route('/workspace')
@login_required
def dashboard():
    return render_template('workspace.html')


if __name__ == '__main__':
    app.run(debug=True)
