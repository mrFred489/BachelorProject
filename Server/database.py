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
    res = np.frombuffer(buf, dtype='int')
    return res


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
    cursor.execute('create table "http://127.0.0.1:5000"(matrix bytea, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001"(matrix bytea, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002"(matrix bytea, id INTEGER, round INTEGER, client text, server text)')
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

def round_one(db_name):
    cur = get_cursor()
    cur.execute(u'SELECT matrix, id, round, client, server '
                u'FROM "' + db_name + '" WHERE round = 1')
    res = []
    for i in cur:
        print("VOTE TAKEN DIRECTLY FROM DATABASE: ", i)
        res.append(i)
    cur.close()
    conn.commit()
    return res


def round_two(db_name):
    cur = get_cursor()
    cur.execute(u'SELECT matrix, id, round, client, server '
                u'FROM "' + db_name + '" WHERE round = 2')
    res = []
    for i in cur:
        res.append(i)
    cur.close()
    conn.commit()
    return res


def insert_vote(matrix: np.ndarray, id: int, round: int, client_name: str, server: str, db_name: str):
    cur = get_cursor()
    print("DTYPE IS: ", matrix.dtype)
    matrix.dtype = np.int64
    cur.execute('INSERT INTO "' + db_name + '" (matrix, id, round, client, server) VALUES (%s, %s, %s, %s, %s)', (matrix, id, round, client_name, server))
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
    cur.execute('insert into "http://127.0.0.1:5000" values (%s, %s, %s, %s, %s)', (temp, 1, 1, "c", "s"))
    cur.close()
    conn.commit()
    cur = get_cursor()
    cur.execute('select * from "http://127.0.0.1:5000"')
    for i in cur:
        print(i)
    cur.close()
