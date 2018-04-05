import os
import psycopg2 as psy
import testing.postgresql
import atexit
import numpy as np
import util


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
    res = np.frombuffer(buf, dtype='float')
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

    # Create table for votes
    cursor.execute('create table "http://127.0.0.1:5000"(matrix text, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001"(matrix text, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002"(matrix text, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5003"(matrix text, id INTEGER, round INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5004"(matrix text, id INTEGER, round INTEGER, client text, server text)')

    # Create table for sums of rows
    cursor.execute('create table "http://127.0.0.1:5000/rows"(row text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001/rows"(row text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002/rows"(row text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5003/rows"(row text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5004/rows"(row text, id INTEGER, type_ text, client text, server text)')

    # Create table for sums of columns
    cursor.execute('create table "http://127.0.0.1:5000/columns"(col text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001/columns"(col text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002/columns"(col text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5003/columns"(col text, id INTEGER, type_ text, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5004/columns"(col text, id INTEGER, type_ text, client text, server text)')

    # Create table for zero_check matrices
    cursor.execute('create table "http://127.0.0.1:5000/zerocheck"(matrix text,  client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001/zerocheck"(matrix text,  client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002/zerocheck"(matrix text,  client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5003/zerocheck"(matrix text,  client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5004/zerocheck"(matrix text,  client text, server text)')

    # Create table for illegal votes
    cursor.execute('create table "http://127.0.0.1:5000/illegal"(sender text, clients text[])')
    cursor.execute('create table "http://127.0.0.1:5001/illegal"(sender text, clients text[])')
    cursor.execute('create table "http://127.0.0.1:5002/illegal"(sender text, clients text[])')
    cursor.execute('create table "http://127.0.0.1:5003/illegal"(sender text, clients text[])')
    cursor.execute('create table "http://127.0.0.1:5004/illegal"(sender text, clients text[])')


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

def round_one(db_name: str):
    cur = get_cursor()
    cur.execute('SELECT matrix, id, round, client, server '
                'FROM "' + db_name + '" WHERE round = 1')
    res = []
    for m, i, r, cl, s in cur:
        m = util.string_to_vote(m)
        res.append((m, i, r, cl, s))
    cur.close()
    conn.commit()
    return res


def round_two(db_name: str):
    cur = get_cursor()
    cur.execute('SELECT matrix, id, round, client, server '
                'FROM "' + db_name + '" WHERE round = 2')
    res = []
    for m, i, r, cl, s in cur:
        m = util.string_to_vote(m)
        res.append((m, i, r, cl, s))
    cur.close()
    conn.commit()
    return res


def get_rows(db_name: str):
    cur = get_cursor()
    cur.execute('SELECT row, id, type_, client, server '
                'FROM "' + db_name + '/rows"')
    res = []
    for r, i, t, cl, s in cur:
        r = util.string_to_vote(r)
        res.append((r, i, t, cl, s))
    cur.close()
    conn.commit()
    return res


def get_cols(table_name: str):
    cur = get_cursor()
    cur.execute('SELECT col, id, type_, client, server '
                'FROM "' + table_name + '/columns"')
    res = []
    for c, i, t, cl, s in cur:
        c = util.string_to_vote(c)
        res.append((c, i, t, cl, s))
    cur.close()
    conn.commit()
    return res


def insert_row(row: np.ndarray, id: int, type_: str, client_name, server, my_name):
    cur = get_cursor()
    row = util.vote_to_string(row)
    cur.execute('INSERT INTO "' + my_name + '/rows" (row, id, type_, client, server) VALUES (%s, %s, %s, %s, %s)',
                (row, id, type_, client_name, server))
    cur.close()
    conn.commit()
    return 1


def insert_col(col: np.ndarray, id: int, type_: str, client_name, server, my_name):
    cur = get_cursor()
    col = util.vote_to_string(col)
    cur.execute('INSERT INTO "' + my_name + '/columns" (col, id, type_, client, server) VALUES (%s, %s, %s, %s, %s)',
                (col, id, type_, client_name, server))
    cur.close()
    conn.commit()
    return 1

def insert_vote(matrix: np.ndarray, id: int, round: int, client_name: str, server: str, db_name: str):
    cur = get_cursor()
    matrix = util.vote_to_string(matrix)
    cur.execute('INSERT INTO "' + db_name + '" (matrix, id, round, client, server) VALUES (%s, %s, %s, %s, %s)', (matrix, id, round, client_name, server))
    cur.close()
    conn.commit()
    return 1

def remove_vote(client_name: str, db_name: str):
    cur = get_cursor()
    cur.execute('DELETE FROM "' + db_name + '" WHERE client=%s', (client_name))
    cur.close()
    conn.commit()
    return 1

def insert_zero_check(matrix: np.ndarray, client_name: str, server: str, db_name: str):
    cur = get_cursor()
    matrix = util.vote_to_string(matrix)
    cur.execute('INSERT INTO "' + db_name + '/zerocheck' + '" (matrix, client, server) VALUES (%s, %s, %s)',
                (matrix, client_name, server))
    cur.close()
    conn.commit()
    return 1

def get_zero_check(db_name: str):
    cur = get_cursor()
    cur.execute('SELECT matrix, client, server FROM "' + db_name + '/zerocheck' + '"')
    res = []
    for m, c, s in cur:
        m = util.string_to_vote(m)
        res.append((m, c, s))
    cur.close()
    conn.commit()
    return res

def insert_illegal_votes(clients: list, sender: str, db_name: str):
    cur = get_cursor()
    cur.execute('INSERT INTO "' + db_name + '/illegal' + '" (sender, clients) VALUES (%s, %s)',
                (sender, clients))
    cur.close()
    conn.commit()
    return 1

def get_illegal_votes(db_name: str):
    cur = get_cursor()
    cur.execute('SELECT sender, clients FROM "' + db_name + '/illegal' + '"')
    res = []
    for i in cur:
        res.append(i)
    cur.close()
    conn.commit()
    return res


def reset(db_name: str):
    cur = get_cursor()

    # TODO: Actually reset table, currently this is not done
    cur.execute('DELETE FROM "' + db_name + '"')
    cur.execute('DELETE FROM "' + db_name + '/columns"')
    cur.execute('DELETE FROM "' + db_name + '/rows"')
    cur.execute('DELETE FROM "' + db_name + '/zerocheck"')
    cur.execute('DELETE FROM "' + db_name + '/illegal"')

    cur.close()
    conn.commit()
    return 1

def reshape_vote(vote):
    if type(vote) == np.ndarray:
        shape = int(np.sqrt(len(vote)))
        return np.reshape(vote, (shape, shape))
    else:
        return 0