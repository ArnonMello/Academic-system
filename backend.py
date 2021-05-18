import os

import sqlalchemy
import pandas as pd
import textract
from flask import Flask, render_template
app = Flask(__name__)


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

    sql_query = f'''Insert Into Artigos
                   (Titulo, Autores,Orientadores,Instituicao,Tipo,PalavrasChave,Resumo, filename)
                   Value ('{titulo}','{autor}','{orientador}','{instituicao}','{tipo}','{palavrasChave}','{resumo}', '{filename}')'''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    conn.execute(sql_query)


def file_to_database(f) -> Artigo:
    path = ''
    path = os.path.join(path, f.filename)
    f.save(path)

    pdf_string = textract.process(path).decode('utf-8')

    artigo = Artigo(titulo=pdf_string.split('\n\n')[5].replace('\n', ' '),
                    autor=pdf_string.split('\n\n')[1].replace('\n', ' & '),
                    orientador=pdf_string.split('\n\n')[7].replace('\n', ' & '),
                    instituicao=pdf_string.split('\n')[3],
                    tipo='PFC',
                    palavrasChave=pdf_string.splitlines()[126].replace('Palavras-chave: ', ''),
                    resumo='\n'.join(pdf_string.split('\n\n')[25][8:].split('\n')[:-1])[:200].replace('\n', ' ') + '...',
                    filename=f.filename)

    artigo_to_database(artigo)

def get_all_filenames():

    query =  '''
    SELECT filename
    FROM Artigos
    '''

    con = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")

    return pd.read_sql_query(query, con)['filename']
