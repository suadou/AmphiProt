from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, BooleanField
from wtforms.validators import InputRequired, Length, Regexp, Optional
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
    PDB_id = StringField('PDB id', validators=[Optional(), Length(min=4, max=4), Regexp("[A-Za-z0-9]", message="PDB id can only contain letters and numbers")])
    UniProt_id = StringField('UniProt id', validators=[Optional(), Length(min=4, max=16), Regexp("[A-Za-z0-9]", message="UniProt id can only contain letters and numbers")])
    sequence = TextAreaField('Sequence', validators=[Optional(), Length(min=50, max=1000)])
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
    data = {}
    if form.PDB_id.data:
        data["PDB_id"] = form.PDB_id.data
    elif form.UniProt_id.data:
        data["UniProt_id"] = form.UniProt_id.data
    elif form.sequence.data:
        data["sequence"] = form.sequence.data
        if check_fasta_input(data["sequence"]) == False:
            flash("FASTA format not correct. Remeber it is mandatory a '>' header. Sequence must contain only amino acids letters.", "error")
            return  render_template('index.html', form=form)
        else:
            data["sequence"]=check_fasta_input(data["sequence"])
            if len(data["sequence"]) < 50 or len(data["sequence"]) > 1000:
                flash("Sequence must contain 50 to 1000 amino acids", "error")
                return  render_template('index.html', form=form)
    else:
        return redirect(url_for('index'))
    data["table"] = form.table.data
    data["BLAST"] = form.BLAST.data
    data["isoelectric"] = form.isoelectric.data
    if form.validate_on_submit():
        if current_user.is_anonymous:
            data["name"] = str(random.randint(1e9, 1e10))
            with open(f"data/{name}/{name}_input.json", 'w') as fp:
                json.dump(data, fp)
                fp.close()
        else:


            with open(f"data/u_{name}/{input_id}_input.json", 'w') as fp:
                json.dump(data, fp)
                fp.close()
                return redirect(url_for('loading'), analysis=current_analysis.analysis_id)
    return  render_template('index.html', form=form)

@app.route('/loading', methods =['GET','POST'])
def loading(analysis, name=None):
    if name:
        data = json.load(f"data/{name}/{name}_input.json")
    else:
        data = json.load(f"data/u_{name}/{input_id}_input.json")

    return render_template('loading.html')


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


@app.route('/help')
def help():
    return render_template('help.html')


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
    

########## Functions ##########################################################

def check_fasta_input(input):
    import re
    seq = ""
    header = False
    for line in input:
        if header:
            seq += line.strip('\n')
        if '>' in line and header == False:
            line = line.strip('\n')
            id = line[1:].strip('\n')
            header = True
        if header == False:
            return False
    alphabets = re.compile('^[acdefghiklmnpqrstvwxy]*$', re.I)
    if alphabets.search(seq) is not None:
         return (id, seq)
    else:
         return False
 def read_table(table_int):
    table = {}
    fd = open("/.../tables/{table_name}", 'r')
    for line in fd:
        line = line.strip()
        (key, val) = line.split(" ")
        table[key] = val
    return table

def fourier(sequence, table, id_user, id_output):
    from numpy import convolve, fft, mean, matrix, square
    from matplotlib import pyplot, transforms
    hydro = [table[aa] for aa in list(sequence)]
    window = 25
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
    pyplot.savefig("Algo/{id_user}/{id_output}_Fourier.png")
    pyplot.figure(figsize=(3, 7))
    km = [1/15] * 15
    base = pyplot.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)
    pyplot.plot(convolve(hydro, km, 'same'), 'r', transform=rot + base)
    pyplot.grid(color='b', linestyle='-', linewidth=0.75)
    pyplot.ylim([1, len(I)])
    pyplot.savefig("Algo/{id_user}/{id_output}_hydroplot.png")



# I left this at the end bc I am not sure if it has to be there?
if __name__ == '__main__':
    app.run(debug=True)
