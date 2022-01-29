from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PotatoPatato'
app.config['SQLALCHEMY_DATABASE_URI'] = 'lalala'
Bootstrap(app)
db = SQLAlchemy(app)


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


class User(db.Model):
    username = db.Column(db.String(25), primary_key=True, unique=True)
    password = db.Column(db.String(80))


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Ampreg = db.Column(db.Boolean)
    Hydro = db.Column(db.Boolean)
    Isopoint = db.Column(db.Boolean)
    Blastp = db.Column(db.Boolean)
    Date = db.Column(db.DateTime)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    impout = db.Column(db.Boolean)
    path = db.Column(db.String(80))
    queryid = db.Column(db.Integer)


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    typetable = db.Column(db.Integer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/loging', methods=['GET', 'POST'])
def loging():
    form = LogingForm()
    return render_template('loging.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
