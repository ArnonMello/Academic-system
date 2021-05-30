import sqlalchemy
import pandas as pd
import fitz
import re


def localizar_pagina(texto, doc):
    pagina = 0
    for page in doc:
        pagina += 1
        if (page.get_text().lower().find(texto) != -1):
            return pagina
    return 0


def extrai_texto_parametro(parametro, page):
    texto = page.get_text()
    param_tamanho = len(parametro)
    param_posicao = texto.lower().find(parametro)
    if param_posicao != -1:
        texto = texto[param_posicao + param_tamanho:]
    return texto


def detectar_tipo(doc):
    tipos = ['pfc', 'projeto', 'tese', 'dissertação']
    tipos_dict = {'pfc': 'pfc', 'projeto': 'pfc', 'tese': 'tese', 'dissertação': 'dis'}
    for tipo in tipos:
        if (doc[1].get_text().lower().find(tipo)) != -1:
            return tipos_dict[tipo]
    return 'tipo nao encontrado'


def retornar_titulo(doc):
    return doc[0].getTextbox(fitz.Rect((0, 400), (600, 650)))


def retornar_autores(doc):
    return doc[0].getTextbox(fitz.Rect((0, 200), (600, 400)))


def retornar_palavras_chave(doc):
    pagina = localizar_pagina("palavras-chave:", doc)
    if (pagina) != 0:
        return extrai_texto_parametro("palavras-chave:", doc[pagina-1])
    return 'palavras-chave nao encontradas'


def retornar_resumo(doc):
    resumo_pagina_numero = localizar_pagina("resumo", doc)
    pagina_resumo = doc[resumo_pagina_numero-1]
    resumo_texto_pagina = pagina_resumo.get_text()
    string = resumo_texto_pagina[resumo_texto_pagina.lower().find("resumo")+6:]
    wrd = 'Palavras-chave:'
    string = string.split()
    res = -1
    for idx in string:
        if len(re.findall(wrd, idx)) > 0:
            res = string.index(idx) + 1
    finalstr = ""
    if(res != -1):
        for i in range(0, res-1):
            finalstr = finalstr + string[i] + " "
    else:
        for i in string:
            finalstr = finalstr + i + " "

    return finalstr[:900]

    # return resumo_texto_pagina[resumo_texto_pagina.lower().find("resumo")+6:]


def retornar_orientadores(doc):
    for pag in doc:
        rect = pag.search_for("orientador")
        if rect:
            rect[0] = fitz.Rect(rect[0].top_left, (rect[0].x1+200, rect[0].y1+50))
            return pag.getTextbox(rect[0])
    return 'nao foram encontrados orientadores'


def retornar_instens(doc):
    capa = doc[0]
    texto = capa.get_text("text")
    string = ""
    crt = 0
    for c in texto:
        if c == "\n":
            crt = crt+1
            continue
        if crt == 3:
            string = string + c
        if crt > 3:
            break
    return string


def get_max_id():
    sql_query = f'''
    SELECT MAX(id)
    FROM Artigos
    '''

    conn = sqlalchemy.create_engine("mysql+mysqldb://bestwinaAdmin:123456789@localhost:3306/pdfLabprog")
    max_id =  pd.read_sql_query(sql_query, conn).iloc[0, 0]
    if max_id is None:
        return -1

    return max_id


def get_pdf_data(fname):
    with fitz.open(fname) as doc:
        titulo = retornar_titulo(doc)
        autores = retornar_autores(doc)
        resumo = retornar_resumo(doc)
        palavras_chave = retornar_palavras_chave(doc)
        tipo = detectar_tipo(doc)
        orientadores = retornar_orientadores(doc)
        inst_end = retornar_instens(doc)
    return {'titulo': titulo, 'autor': autores, 'resumo': resumo, 'palavrasChave': palavras_chave,
            'tipo': tipo,  'orientador': orientadores, 'instituicao': inst_end, 'filename': fname,
            'id': get_max_id()+1}
