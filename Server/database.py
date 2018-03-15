import os
import psycopg2 as psy
import testing.postgresql
import atexit
import numpy as np


test = False
if str(os.path.dirname(__file__).split("/")[-2]) != "flaskwebsite":
    test = True


def adapt_array(a):
    return psy.Binary(a)


psy.extensions.register_adapter(np.ndarray, adapt_array)


def typecast_array(data, cur):
    if data is None:
        return None
    buf = psy.BINARY(data, cur)
    return np.frombuffer(buf)


ARRAY = psy.extensions.new_type(psy.BINARY.values,
'ARRAY', typecast_array)


psy.extensions.register_type(ARRAY)


if not test:
    conn = psy.connect(host='localhost', user='bachelor', password='gruppen1234', dbname='bachelorprojekt')


    def get_conn():
        global conn
        conn = psy.connect(host='localhost', user='bachelor', passwd='gruppen1234', dbname='bachelorprojekt')

else:
    postgresql = testing.postgresql.Postgresql()
    conn = psy.connect(**postgresql.dsn())
    cursor = conn.cursor()
    # cursor.execute('create table "http://127.0.0.1:5000"(name text, number INTEGER, client text, server text, id INTEGER )')
    # cursor.execute('create table "http://127.0.0.1:5001"(name text, number INTEGER, client text, server text, id INTEGER)')
    # cursor.execute('create table "http://127.0.0.1:5002"(name text, number INTEGER, client text, server text, id INTEGER)')
    cursor.execute('create table "http://127.0.0.1:5000"(matrix bytea, id INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001"(matrix bytea, id INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002"(matrix bytea, id INTEGER, client text, server text)')
    cursor.close()
    conn.commit()
    print("DATABASES UP AND RUNNING")

    def get_conn():
        global conn
        conn = psy.connect(postgresql.dsn())

    def cleanup():
        print("cleanup")
        postgresql.stop()

    atexit.register(cleanup)


def get_cursor():
    global conn
    try:
        cursor = conn.cursor()
        cursor.execute("select 1;")
    except psy.OperationalError:
        get_conn()
        cursor = conn.cursor()
    return cursor

def get_votes(db_name):
    cur = get_cursor()
    cur.execute(u'SELECT matrix, id, client, server FROM "' + db_name + '"')
    res = []
    for i in cur:
        res.append(i)
    cur.close()
    conn.commit()
    return res

#
# def insert_number(num: int, name: str, id: int, client, server, db_name: str):
#     cur = get_cursor()
#     query = u'INSERT INTO "' + db_name + '" (number, name, id, client, server) VALUES (' \
#             + str(num) + ', \'' + name + '\', \'' + str(id) + '\', \'' + client + '\', \'' + server + '\')'
#     cur.execute(query)
#     cur.close()
#     conn.commit()
#     return 1


def get_ri_values(db_name):
    cur = get_cursor()
    query = u'SELECT matrix, id,client,server FROM "' + db_name + '"'
    cur.execute(query)
    cur.close()
    conn.commit()


def insert_vote(matrix: np.ndarray, id: int, client_name: str, server: str, db_name: str):
    cur = get_cursor()
    cur.execute('INSERT INTO "' + db_name + '" (matrix, id, client, server) VALUES (%s, %s, %s, %s)', (matrix, id, client_name, server))
    cur.close()
    conn.commit()
    return 1

def reset(db_name: str):
    cur = get_cursor()

    cur.execute(u'DELETE FROM "' + db_name + '"')

    cur.close()
    conn.commit()

    return 1


if __name__ == "__main__":
    temp = np.zeros((3,4))
    cur = get_cursor()
    cur.execute('insert into "http://127.0.0.1:5000" values (%s, %s, %s, %s)', (temp, 1, "c", "s"))
    cur.close()
    conn.commit()
    cur = get_cursor()
    cur.execute('select * from "http://127.0.0.1:5000"')
    for i in cur:
        print(i)
    cur.close()
