import os
import psycopg2 as psy
import testing.postgresql
import atexit
import numpy as np
import util
from collections import defaultdict

test = False
if str(os.path.dirname(__file__).split("/")[-2]) != "flaskwebsite":
    test = True

if not test:
    conn = psy.connect(host='localhost', user='bachelor', password='gruppen1234', dbname='bachelorprojekt')
    mediator = "http://127.0.0.1:5100"

    def get_conn():
        global conn
        conn = psy.connect(host='localhost', user='bachelor', passwd='gruppen1234', dbname='bachelorprojekt')

else:
    postgresql = testing.postgresql.Postgresql()
    conn = psy.connect(**postgresql.dsn())
    cursor = conn.cursor()
    mediator = "http://127.0.0.1:5100"

    def get_conn():
        global conn
        conn = psy.connect(**postgresql.dsn())

    # Create tables for votes
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000"(matrix TEXT, id INTEGER, round INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001"(matrix TEXT, id INTEGER, round INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002"(matrix TEXT, id INTEGER, round INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003"(matrix TEXT, id INTEGER, round INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004"(matrix TEXT, id INTEGER, round INTEGER, client TEXT, server TEXT)')

    #Create tables for results
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/result"(matrix TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/result"(matrix TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/result"(matrix TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/result"(matrix TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/result"(matrix TEXT, server TEXT)')


    # Create table for sums of rows
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/rows"(row TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/rows"(row TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/rows"(row TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/rows"(row TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/rows"(row TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')

    # Create table for sums of columns
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/columns"(col TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/columns"(col TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/columns"(col TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/columns"(col TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/columns"(col TEXT, id INTEGER, type_ TEXT, client TEXT, server TEXT)')

    # Create table for zero_partitions
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/zeropartition"(matrix TEXT, client TEXT, server TEXT, x INTEGER, i INTEGER, j INTEGER)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/zeropartition"(matrix TEXT, client TEXT, server TEXT, x INTEGER, i INTEGER, j INTEGER)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/zeropartition"(matrix TEXT, client TEXT, server TEXT, x INTEGER, i INTEGER, j INTEGER)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/zeropartition"(matrix TEXT, client TEXT, server TEXT, x INTEGER, i INTEGER, j INTEGER)')

    # Create table for zero_one_consistency_check matrices
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/zeroconsistency"(diff TEXT, x INTEGER, i INTEGER, j INTEGER, server_a TEXT, server_b TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/zeroconsistency"(diff TEXT, x INTEGER, i INTEGER, j INTEGER, server_a TEXT, server_b TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/zeroconsistency"(diff TEXT, x INTEGER, i INTEGER, j INTEGER, server_a TEXT, server_b TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/zeroconsistency"(diff TEXT, x INTEGER, i INTEGER, j INTEGER, server_a TEXT, server_b TEXT, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/zeroconsistency"(diff TEXT, x INTEGER, i INTEGER, j INTEGER, server_a TEXT, server_b TEXT, client TEXT, server TEXT)')

    # Create table for zero_one_partition_sum matrices
    cursor.execute('CREATE TABLE "http://127.0.0.1:5000/zeropartitionsum"(matrix TEXT, client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5001/zeropartitionsum"(matrix TEXT, client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5002/zeropartitionsum"(matrix TEXT, client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5003/zeropartitionsum"(matrix TEXT, client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5004/zeropartitionsum"(matrix TEXT, client TEXT, server TEXT)')


    # Create table for zero_check matrices
    cursor.execute('CREATE TABLE "http://127.0.0.1:5000/zerocheck"(matrix TEXT,  client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5001/zerocheck"(matrix TEXT,  client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5002/zerocheck"(matrix TEXT,  client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5003/zerocheck"(matrix TEXT,  client TEXT, server TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5004/zerocheck"(matrix TEXT,  client TEXT, server TEXT)')

    # Create table for illegal votes
    cursor.execute('CREATE TABLE "http://127.0.0.1:5000/illegal"(sender TEXT, clients TEXT[])')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5001/illegal"(sender TEXT, clients TEXT[])')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5002/illegal"(sender TEXT, clients TEXT[])')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5003/illegal"(sender TEXT, clients TEXT[])')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5004/illegal"(sender TEXT, clients TEXT[])')

    # Create tables for summed votes
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/summed_votes"(matrix TEXT, id INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/summed_votes"(matrix TEXT, id INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/summed_votes"(matrix TEXT, id INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/summed_votes"(matrix TEXT, id INTEGER, client TEXT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/summed_votes"(matrix TEXT, id INTEGER, client TEXT, server TEXT)')

        # Create tables for summed diffs
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5000/summed_diffs"(diffs TEXT, client TEXT, i INT, j INT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5001/summed_diffs"(diffs TEXT, client TEXT, i INT, j INT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5002/summed_diffs"(diffs TEXT, client TEXT, i INT, j INT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5003/summed_diffs"(diffs TEXT, client TEXT, i INT, j INT, server TEXT)')
    cursor.execute(
        'CREATE TABLE "http://127.0.0.1:5004/summed_diffs"(diffs TEXT, client TEXT, i INT, j INT, server TEXT)')


    # Create tables for the mediator
    cursor.execute('CREATE TABLE "http://127.0.0.1:5100/illegal"(sender TEXT, clients TEXT[])')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5100/inconsistency"(sender TEXT, complaint TEXT, protocol TEXT)')
    cursor.execute('CREATE TABLE "http://127.0.0.1:5100/inconsistency_extra_data"(sender TEXT, complaint TEXT, protocol TEXT, data TEXT)')

    cursor.close()
    conn.commit()
    print("DATABASES UP AND RUNNING\n")



    def cleanup():
        print("cleanup")
        postgresql.stop()

    atexit.register(cleanup)


def db_execute(cnn, query):
    global conn
    try:
        cursor = cnn.cursor()
        cursor.execute(query)
    except:
        conn = psy.connect(**postgresql.dsn())
        cursor = conn.cursor()
        cursor.execute(query)
    return cursor


def db_execute_extra(cnn, query, extra):
    global conn
    try:
        cursor = cnn.cursor()
        cursor.execute(query, extra)
    except:
        conn = psy.connect(**postgresql.dsn())
        cursor = conn.cursor()
        cursor.execute(query, extra)
    return cursor



def get_cursor():
    global conn
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
    except psy.OperationalError as e:
        print("Caught psy.OperationalError:")
        print(e)
        get_conn()
        cursor = conn.cursor()
    except:
        print("Caught error")
        get_conn()
        cursor = conn.cursor()
    return cursor


def round_one(db_name: str):
    cur = db_execute(conn, 'SELECT matrix, id, round, client, server FROM "' + db_name + '" WHERE round = 1')
    res = []
    for m, i, r, cl, s in cur:
        m = util.string_to_vote(m)
        res.append((m, i, r, cl, s))
    cur.close()
    conn.commit()
    return res


def round_two(db_name: str):
    cur = db_execute(conn, 'SELECT matrix, id, client, server FROM "' + db_name + '/summed_votes"')
    res = []
    for m, i, cl, s in cur:
        m = util.string_to_vote(m)
        res.append((m, i, cl, s))
    cur.close()
    conn.commit()
    return res


def get_rows(db_name: str):
    cur = db_execute(conn, 'SELECT row, id, type_, client, server FROM "' + db_name + '/rows"')
    res = []
    for r, i, t, cl, s in cur:
        r = util.string_to_vote(r)
        res.append((r, i, t, cl, s))
    cur.close()
    return res


def get_cols(table_name: str):
    cur = db_execute(conn, 'SELECT col, id, type_, client, server FROM "' + table_name + '/columns"')
    res = []
    try:
        for (c, i, t, cl, s) in cur:
            c = util.string_to_vote(c)
            res.append((c, i, t, cl, s))
    except psy.ProgrammingError:
        res = []
    cur.close()
    return res


def insert_row(row: np.ndarray, id: int, type_: str, client_name, server, my_name):
    row = util.vote_to_string(row)
    cur = db_execute(conn, 'SELECT row FROM "' + my_name + '/rows" WHERE id = ' + str(id) + ' AND client = \'' + str(client_name) + '\' AND server = \'' + str(server) + '\'')
    if len(cur.fetchall()) == 0:
        cur = db_execute_extra(conn, 'INSERT INTO "' + my_name + '/rows" (row, id, type_, client, server) VALUES (%s, %s, %s, %s, %s)',
                    (row, id, type_, client_name, server))
    else:
        cur.execute('UPDATE "' + my_name + '/rows" SET row = \'' + row + '\' WHERE id = ' + str(
            id) + ' AND client = \'' + str(client_name) + '\' AND server = \'' + str(server) + '\'')
    cur.close()
    conn.commit()
    return 1


def insert_col(col: np.ndarray, id: int, type_: str, client_name, server, my_name):
    col = util.vote_to_string(col)
    cur = db_execute(conn, 'SELECT col FROM "' + my_name + '/columns" WHERE id = ' + str(id) + ' AND client = \'' + str(client_name) + '\' AND server = \'' + str(server) + '\'')
    if len(cur.fetchall()) == 0:
        cur = db_execute_extra(conn, 'INSERT INTO "' + my_name + '/columns" (col, id, type_, client, server) VALUES (%s, %s, %s, %s, %s)',
                    (col, id, type_, client_name, server))
    else:
        cur = db_execute(conn, 'UPDATE "' + my_name + '/columns" SET col = \'' + col + '\' WHERE id = ' + str(id) + ' AND client = \'' + str(client_name) + '\' AND server = \'' + str(server) + '\'')
    cur.close()
    conn.commit()
    return 1


def insert_vote(matrix: np.ndarray, id: int, round: int, client_name: str, server: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute(conn, 'SELECT matrix FROM "' + db_name + '" WHERE id = ' + str(id)
                + ' AND client = \'' + str(client_name)
                + '\' AND server = \'' + str(server)
                + '\' AND round = ' + str(round))
    if len(cur.fetchall()) == 0:
        cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '" (matrix, id, round, client, server) VALUES (%s, %s, %s, %s, %s)',
                (matrix, id, round, client_name, server))
    else:
        cur = db_execute(conn, 'UPDATE "' + db_name + '" SET matrix = \'' + matrix
                    + '\' WHERE id = ' + str(id)
                    + ' AND client = \'' + str(client_name)
                    + '\' AND server = \'' + str(server)
                    + '\' AND round = ' + str(round))
    cur.close()
    conn.commit()
    return 1


def remove_vote(client_name: str, db_name: str):
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '" WHERE client = \'' + str(client_name) + '\'')
    cur.close()
    conn.commit()
    return 1


def insert_summed_votes(matrix: np.ndarray, id: int, client_name: str, server: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/summed_votes" (matrix, id, client, server) VALUES (%s, %s, %s, %s)',
                (matrix, id, client_name, server))
    cur.close()
    conn.commit()
    return 1


def insert_summed_diffs(diffs: list, client_name: str, i: int, j: int, server: str):
    diffs = util.vote_to_string(diffs)
    cur = db_execute_extra(conn, 'INSERT INTO "' + server + '/summed_diffs" (diffs, client, i, j, server) VALUES (%s, %s, %s, %s, %s)',
                (diffs, client_name, i, j, server))
    cur.close()
    conn.commit()
    return 1


def get_summed_diffs(db_name: str):
    cur = db_execute(conn, 'SELECT diffs, client, i, j, server FROM "' + db_name + '/summed_diffs"')
    res = []
    for d, c, i, j, s in cur:
        d = util.string_to_vote(d)
        res.append((d, c, i, j, s))
    cur.close()
    conn.commit()
    return res


def insert_result(matrix: np.ndarray, server: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/result" (matrix, server) '
                + 'VALUES (%s, %s)',
                (matrix, server))
    cur.close()
    conn.commit()
    return 1


def get_results(db_name: str):
    cur = db_execute(conn, 'SELECT matrix, server FROM "' + db_name + '/result"')
    res = []
    for m, s in cur:
        m = util.string_to_vote(m)
        res.append((m, s))
    cur.close()
    conn.commit()
    return res


def get_results_count(db_name: str):
    cur = db_execute(conn, 'SELECT COUNT(*) FROM (SELECT DISTINCT matrix FROM "' + db_name + '/result") AS temp')
    res = cur.fetchone()[0]
    cur.close()
    conn.commit()
    return res



def insert_zero_partition(matrix: np.ndarray, x: int, i: int, j: int, client_name: str, server: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute(conn, 'SELECT matrix FROM "' + db_name + '/zeropartition" WHERE client = \'' + str(client_name)
                + '\' AND x = \'' + str(x)
                + '\' AND i = \'' + str(i)
                + '\' AND j = \'' + str(j)
                + '\' AND server = \'' + str(server) + '\'')
    if len(cur.fetchall()) == 0:
        cur = db_execute_extra(conn, 
            'INSERT INTO "' + db_name + '/zeropartition" (matrix, client, server, x, i, j) VALUES (%s, %s, %s, %s, %s, %s)',
            (matrix, client_name, server, x, i, j))
    else:
        cur = db_execute(conn, 'UPDATE "' + db_name + '/zeropartition" SET matrix = \'' + matrix
                    + '\' WHERE client = \'' + str(client_name)
                    + '\' AND server = \'' + str(server)
                    + '\' AND x = \'' + str(x)
                    + '\' AND i = \'' + str(i)
                    + '\' AND j = \'' + str(j) + '\'')
    cur.close()
    conn.commit()
    return 1

def get_zero_partitions(db_name: str):
    cur = db_execute(conn, 'SELECT matrix, client, server, x, i, j FROM "' + db_name + '/zeropartition"')
    res = defaultdict(list)
    for m, c, s, x, i, j in cur:
        res[c]
        m = util.string_to_vote(m)
        res[c].append(dict(matrix=m, x=x, i=i, j=j, server=s))
    cur.close()
    conn.commit()
    return res

def insert_zero_partition_sum(matrix: np.ndarray, server: str, client: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/zeropartitionsum" (matrix, client, server) VALUES (%s, %s, %s)',
                (matrix, client, server))
    cur.close()
    conn.commit()
    return 1

def get_zero_partition_sum(db_name):
    cur = db_execute(conn, 'SELECT matrix, client, server FROM "' + db_name + '/zeropartitionsum"')
    res = defaultdict(list)
    for m, c, s in cur:
        res[c]
        m = util.string_to_vote(m)
        res[c].append(dict(matrix=m, server=s))
    cur.close()
    conn.commit()
    return res


def insert_zero_consistency_check(diff: np.ndarray, x: int, i: int, j:int, server_a: str, server_b: str, client_name: str, server: str, db_name: str):
    diff = util.vote_to_string(diff)
    cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/zeroconsistency" (diff, x, i, j, server_a, server_b, client, server) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (diff, x, i, j, server_a, server_b, client_name, server))
    cur.close()
    conn.commit()
    return 1

def get_zero_consistency_check(db_name: str):
    cur = db_execute(conn, 'SELECT diff, x, i, j, server_a, server_b, client, server FROM "' + db_name + '/zeroconsistency"')
    res = defaultdict(list)
    for d, x, i, j, sa, sb, c, s in cur:
        d = util.string_to_vote(d)
        res[c].append(dict(diff=d, x=x, i=i, j=j, server_a=sa, server_b=sb, server=s))
    cur.close()
    conn.commit()
    return res


def get_zero_consistency_check_alt(db_name: str):
    cur = db_execute(conn, 'SELECT diff, x, i, j, server_a, server_b, client, server FROM "' + db_name + '/zeroconsistency"')
    res = []
    for d, x, i, j, sa, sb, c, s in cur:
        d = util.string_to_vote(d)
        res.append((d, c, i, j, x, sa, sb, s))
    cur.close()
    conn.commit()
    return res


def insert_zero_check(matrix: np.ndarray, client_name: str, server: str, db_name: str):
    matrix = util.vote_to_string(matrix)
    cur = db_execute(conn, 'SELECT matrix FROM "' + db_name + '/zerocheck" WHERE client = \'' + str(
        client_name) + '\' AND server = \'' + str(server) + '\'')
    if len(cur.fetchall()) == 0:
        cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/zerocheck' + '" (matrix, client, server) VALUES (%s, %s, %s)',
                    (matrix, client_name, server))
    else:
        cur = db_execute(conn, 
            'UPDATE "' + db_name + '/zerocheck" SET matrix = \'' + matrix + '\' WHERE client = \'' + str(
                client_name) + '\' AND server = \'' + str(server) + '\'')
    cur.close()
    conn.commit()
    return 1


def get_zero_check(db_name: str):
    cur = db_execute(conn, 'SELECT matrix, client, server FROM "' + db_name + '/zerocheck' + '"')
    res = []
    for m, c, s in cur:
        m = util.string_to_vote(m)
        res.append((m, c, s))
    cur.close()
    conn.commit()
    return res

def insert_illegal_votes(clients: list, sender: str, db_name: str):
    cur = db_execute_extra(conn, 'INSERT INTO "' + db_name + '/illegal' + '" (sender, clients) VALUES (%s, %s)',
                (sender, clients))
    cur.close()
    conn.commit()
    return 1


def get_illegal_votes(db_name: str):
    cur = db_execute(conn, 'SELECT sender, clients FROM "' + db_name + '/illegal' + '"')
    res = []
    try:
        for i in cur:
            res.append(i)
        cur.close()

    except psy.ProgrammingError:
        res = []
    return res




def insert_mediator_illegal_votes(clients: list, sender: str):
    cur = db_execute_extra(conn, 'INSERT INTO "' + mediator + '/illegal' + '" (sender, clients) VALUES (%s, %s)',
                (sender, clients))
    cur.close()
    conn.commit()
    return 1


def get_mediator_illegal_votes():
    cur = db_execute(conn, 'SELECT sender, clients FROM "' + mediator + '/illegal' + '"')
    res = []
    for i in cur:
        res.append(i)
    cur.close()
    return res




def insert_mediator_inconsistency(sender: str, complaint: util.Complaint, protocol: util.Protocol):
    complaint = util.vote_to_string(complaint)
    cur = db_execute_extra(conn, 'INSERT INTO "' + mediator + '/inconsistency' + '" (sender, complaint, protocol) VALUES (%s, %s, %s)',(sender, complaint, protocol.value))
    cur.close()
    conn.commit()
    return 1


def get_mediator_inconsistency():
    cur = db_execute(conn, 'SELECT sender, complaint, protocol FROM "' + mediator + '/inconsistency' + '"')
    res = []
    try: 
        for s, c, p in cur:
            res.append((s, util.string_to_vote(c), util.Protocol(int(p))))
    except psy.ProgrammingError:
        res = []
    cur.close()
    return res


def insert_mediator_inconsistency_extra_data(sender: str, complaint: util.Complaint, protocol: util.Protocol, data: dict):
    complaint = util.vote_to_string(complaint)
    data = util.vote_to_string(data)
    cur = db_execute_extra(conn, 'INSERT INTO "' + mediator + '/inconsistency_extra_data' + '" (sender, complaint, protocol, data) VALUES (%s, %s, %s, %s)',(sender, complaint, protocol.value, data))
    cur.close()
    conn.commit()
    return 1


def get_mediator_inconsistency_extra_data():
    cur = db_execute(conn, 'SELECT sender, complaint, protocol, data FROM "' + mediator + '/inconsistency_extra_data' + '"')
    res = []
    for s, c, p, d in cur:
        res.append((s, util.string_to_vote(c), util.Protocol(int(p)), util.string_to_vote(d)))
    cur.close()
    conn.commit()
    return res


def reset(db_name: str):

    cur = db_execute(conn, 'DELETE FROM "' + db_name + '"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/result"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/rows"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/columns"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/zeropartition"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/zeroconsistency"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/zeropartitionsum"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/zerocheck"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/illegal"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/summed_votes"')
    cur = db_execute(conn, 'DELETE FROM "' + db_name + '/summed_diffs"')


    cur.close()
    conn.commit()
    return 1

def reset_mediator():
    cur = get_cursor()
    cur.execute('DELETE FROM "' + mediator + '/illegal"')
    cur.execute('DELETE FROM "' + mediator + '/inconsistency"')
    cur.execute('DELETE FROM "' + mediator + '/inconsistency_extra_data"')
    cur.close()
    conn.commit()
    return 1


def reshape_vote(vote):
    if type(vote) == np.ndarray:
        shape = int(np.sqrt(len(vote)))
        return np.reshape(vote, (shape, shape))
    else:
        return 0
