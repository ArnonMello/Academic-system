
import pyodbc
from flask import Flask, render_template
app = Flask(__name__)



@app.route('/')
def hello():
    return render_template('index.html')

def pdfToDatabase(artigo):
    titulo=artigo.titulo
    autor=artigo.autores
    orientador=artigo.orientidador
    instituicao=artigo.instituicao
    tipo=artigo.tipo
    palavrasChave=artigo.palavrasChave
    resumo=artigo.resumo

    sql_query= f'''Insert Into Artigos
                   (Titulo, Autores,Orientadores,Instituicao,Tipo,PalavrasChave,Resumo)
                   Value ('{titulo}','{autor}','{orientador}','{instituicao}','{tipo}','{palavrasChave}','{resumo}')'''
    
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=localhost;'
                      'Database=pdfLabprog;'
                      'Trusted_Connection=yes;')

    cursor = conn.cursor()
    cursor.execute(sql_query)

