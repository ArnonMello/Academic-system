import zipfile
import requests
import sqlalchemy
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
import pandas as pd
from flask import send_from_directory
from backend import User, file_to_database, get_all_filenames

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


users = []
users.append(User(id=1, username='admin', password='password'))
users.append(User(id=2, username='coordenador', password='password'))
users.append(User(id=3, username='joao', password='password'))


@app.route('/')
def main():
    return redirect(url_for('login'))


@app.route('/index')
def index():
    db = getDB()
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

    if 'user_id' in session:
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


def getDB():
    sql_query = '''Select * from Artigos'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    db = pd.read_sql_query(sql_query, conn)
    db_dict = db.T.to_dict().values()
    return db_dict
