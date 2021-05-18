import sqlalchemy
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import pandas as pd
from flask import send_from_directory
import os
import textract

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


class Artigo:
    def __init__(self, titulo, autor, orientador, instituicao, tipo, palavrasChave, resumo, filename):
        self.titulo = titulo
        self.autor = autor
        self.orientador = orientador
        self.instituicao = instituicao
        self.tipo = tipo
        self.palavrasChave = palavrasChave
        self.resumo = resumo
        self.filename = filename


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
        f = request.files['file']
        path = ''
        path = os.path.join(path, f.filename)
        f.save(path)
        text = textract.process(path)
        linhas = text.decode('utf8').splitlines()
        textos = []
        for linha in linhas:
            if linha != '':
                splitted = linha.split(':')
                textos.append(splitted[1])

        artigo = Artigo(textos[0], textos[1], textos[2], textos[3], textos[4], textos[5], textos[6], f.filename)
        pdfToDatabase(artigo)

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


def pdfToDatabase(artigo):
    titulo = artigo.titulo
    autor = artigo.autor
    orientador = artigo.orientador
    instituicao = artigo.instituicao
    tipo = artigo.tipo
    palavrasChave = artigo.palavrasChave
    resumo = artigo.resumo
    filename = artigo.filename

    sql_query = f'''Insert Into Artigos
                   (Titulo, Autores,Orientadores,Instituicao,Tipo,PalavrasChave,Resumo, filename)
                   Value ('{titulo}','{autor}','{orientador}','{instituicao}','{tipo}','{palavrasChave}','{resumo}','{filename}')'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    conn.execute(sql_query)


def getDB():
    sql_query = '''Select * from Artigos'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    db = pd.read_sql_query(sql_query, conn)
    db_dict = db.T.to_dict().values()
    return db_dict
