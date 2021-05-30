from os import listdir
from os.path import isfile, join
import zipfile
import os

import sqlalchemy
import pandas as pd
from flask import Flask, render_template
from helper import get_pdf_data
app = Flask(__name__)


class Artigo:
    def __init__(self, id, titulo, autor, orientador, instituicao, tipo, palavrasChave, resumo, filename):
        self.titulo = titulo
        self.autor = autor
        self.orientador = orientador
        self.instituicao = instituicao
        self.tipo = tipo
        self.palavrasChave = palavrasChave
        self.resumo = resumo
        self.filename = filename
        self.id = id


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


@app.route('/')
def hello():
    return render_template('index.html')


def artigo_to_database(artigo):
    titulo = artigo.titulo
    autor = artigo.autor
    orientador = artigo.orientador
    instituicao = artigo.instituicao
    tipo = artigo.tipo
    palavrasChave = artigo.palavrasChave
    resumo = artigo.resumo
    filename = artigo.filename
    id = artigo.id

    sql_query = f'''Insert Into Artigos
                   (Titulo, Autores,Orientadores,Instituicao,Tipo,PalavrasChave,Resumo, filename, id)
                   Value ('{titulo}','{autor}','{orientador}','{instituicao}','{tipo}','{palavrasChave}','{resumo}', '{filename}', {id})'''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)


def file_to_database(f) -> Artigo:
    path = ''
    path = os.path.join(path, f.filename)
    f.save(path)

    artigo = Artigo(**get_pdf_data(path))

    artigo_to_database(artigo)


def get_all_filenames():

    query = '''
    SELECT filename
    FROM Artigos
    '''

    con = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    return pd.read_sql_query(query, con)['filename']


def getDB():
    sql_query = '''Select * from Artigos'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    db = pd.read_sql_query(sql_query, conn)
    db_dict = db.T.to_dict().values()
    return db_dict


def get_data_from_id(id):
    sql_query = f'''Select * from Artigos where id={id}'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    db = pd.read_sql_query(sql_query, conn).iloc[0]
    return db.squeeze().to_dict()


def alter_artigo(request_form):

    sql_query = f'''
    UPDATE Artigos
    SET Titulo = '{request_form.get('titulo')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET Autores = '{request_form.get('autor')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET Orientadores = '{request_form.get('orientador')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET Instituicao = '{request_form.get('instituicao')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET Tipo = '{request_form.get('tipo')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET PalavrasChave = '{request_form.get('palavrasChave')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)

    sql_query = f'''
    UPDATE Artigos
    SET Resumo = '{request_form.get('resumo')}'
    WHERE id = {request_form.get('id')}
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)


def tableUsers():
    sql_query = '''Select * from usernames'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    db = pd.read_sql_query(sql_query, conn)

    return db


def getUsers():
    users = []

    db = tableUsers()
    print(db)
    for index, row in db.iterrows():
        users.append(User(id=int(row['PersonID']), username=row['username'], password=row['password']))

    return users


def registerUser(personID, username, password):

    sql_query = f'''Insert into usernames (PersonID, username, password)
                    Value({personID},'{username}','{password}')'''

    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    conn = conn.raw_connection()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()
    cursor.close()
    conn.close()


def restoreDatabase():
    # Extrair o zip para a pasta arquivos
    with zipfile.ZipFile('backup.zip', 'r') as zip_ref:
        zip_ref.extractall('./')

    os.remove('backup.zip')

    users = pd.read_excel('arquivos/users.xlsx')
    print(users)
    # Deletar o excel users
    os.remove('arquivos/users.xlsx')

    # Inserir users na tabela
    for index, row in users.iterrows():
        registerUser(row['PersonID'], row['username'], row['password'])

    # Colocar aquivos no bd
    files = [f for f in listdir('arquivos') if isfile(join('arquivos', f))]

    for filename in files:
        if filename.find('.pdf') >= 0:
            file_to_database(filename, create=True)

    # return "Success"


def deleteDatabase():

    sql_delete_artigos = 'Delete from Artigos'
    sql_delete_users = 'Delete from usernames'
    conn = sqlalchemy.create_engine('mysql+mysqldb://bestwinaAdmin:123456789@127.0.0.1:3306/pdfLabprog')  # connect to server
    conn = conn.raw_connection()
    cursor = conn.cursor()
    cursor.execute(sql_delete_artigos)
    cursor.execute(sql_delete_users)
    conn.commit()
    cursor.close()
    conn.close()
