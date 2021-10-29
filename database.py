import sqlite3
URL_DB = 'Eccomerce.db'

def seleccion(sql) -> list:
    """ Ejecuta una consulta de selección sobre la base de datos """
    print(f'query ejecutado: {sql}')
    try:
        with sqlite3.connect(URL_DB) as con:
            cur = con.cursor()
            res = cur.execute(sql).fetchall()
    except Exception:
        res = None
    return res

def seleccionSecure(sql, datos) -> list:
    """ Ejecuta una consulta de selección sobre la base de datos, usando parámetros nombrados """
    print(f'query ejecutado secure: {sql}, data: {datos}')
    try:
        with sqlite3.connect(URL_DB) as con:
            cur = con.cursor()
            res = cur.execute(sql, datos).fetchall()
               
    except Exception as ex:
        template = "SQLite: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        res = None
        print(message)

    return res


def accion(sql, datos) -> int:
    """ Ejecuta una consulta de acción sobre la base de datos """
    try:
        print(f'query ejecutado (acción): {sql}')
        with sqlite3.connect(URL_DB) as con:
            cur = con.cursor()
            res = cur.execute(sql,datos).rowcount
            if res!=0:
                con.commit()
    except Exception:
        res = 0
    return res
