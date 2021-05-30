import os
import zipfile
from flask import (
    Flask,
    send_file,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask import send_from_directory
from flask_session import Session
from flask_cors import CORS
from backend import User, file_to_database, get_all_filenames, getDB, get_data_from_id, alter_artigo, restoreDatabase

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
CORS(app)


users = []
global_user = User(id=2, username='joao', password='maria')
users.append(User(id=1, username='admin', password='password'))
users.append(User(id=2, username='coordenador', password='password'))
users.append(User(id=3, username='joao', password='password'))


@app.route('/')
def main():
    return redirect(url_for('login'))


@app.route('/index')
def index():
    db = getDB()
    session['user_id'] = session.get('user_id')
    return render_template('index.html', db=db)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        file_to_database(request.files['file'])

        db = getDB()
        return render_template('index.html', db=db)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        db = getDB()
        db = [x for x in db if request.form['search_bar'] in x['Titulo'].upper()]
        return render_template('index.html', db=db)


@app.route('/download', methods=["GET", "POST"])
def download():
    if request.method == 'POST':

        filename = request.form.get('filename')
        uploads = ''
        return send_from_directory(directory=uploads, filename=filename)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


@app.route('/restore', methods=["GET", "POST"])
def restore():

    if request.method == 'POST' and global_user.id == 2:
        # Restaurar banco de dados
        restoreDatabase()
        return redirect(url_for('index'))

    return "Usuário sem permissão"


@app.route('/alterar', methods=["GET", "POST"])
def alterar():
    if request.method == 'POST':
        id = request.form.get('id')

        data = get_data_from_id(id)

        return render_template('alter.html', data=data)


@app.route('/alterar_form', methods=["GET", "POST"])
def alterar_form():
    if request.method == 'POST':
        print(request.form)

        alter_artigo(request.form)

        return redirect(url_for('index'))


@app.route('/backup', methods=["GET", "POST"])
def backup():
    if request.method == 'POST':

        f_names = get_all_filenames()

        zipf = zipfile.ZipFile("backup.zip", "w", zipfile.ZIP_DEFLATED)

        for fn in f_names:
            zipf.write(fn)

        return send_file("backup.zip", mimetype="zip",
                         attachment_filename="backup.zip",
                         as_attachment=True)

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session.keys():
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def sigup():


    if request.method == 'GET':

        id_user = session['user_id']
        if id_user in [1,2]:
            return render_template('signup.html')
        else:
            return 'Usuário sem permissão'

    if request.method == 'POST':

        if session['user_id']!=2:
            return "Usuário sem permissão"
        print(request.form)
        personID = request.form['personID']
        username = request.form['username']
        password = request.form['password']
        registerUser(personID,username,password)
        return 'Usuário registrado!'


