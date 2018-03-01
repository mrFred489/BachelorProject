import os
import psycopg2 as psy
import testing.postgresql
import atexit


test = False
if str(os.path.dirname(__file__).split("/")[-2]) != "flaskwebsite":
    test = True

if not test:
    conn = psy.connect(host='localhost', user='bachelor', password='gruppen1234', dbname='bachelorprojekt')


    def get_conn():
        global conn
        conn = psy.connect(host='localhost', user='bachelor', passwd='gruppen1234', dbname='bachelorprojekt')

else:
    postgresql = testing.postgresql.Postgresql()
    conn = psy.connect(**postgresql.dsn())
    cursor = conn.cursor()
    cursor.execute('create table "http://127.0.0.1:5000"(name text, number INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5001"(name text, number INTEGER, client text, server text)')
    cursor.execute('create table "http://127.0.0.1:5002"(name text, number INTEGER, client text, server text)')
    cursor.close()
    conn.commit()

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


def get_numbers(db_name):
    cur = get_cursor()
    cur.execute(u'SELECT number,name,client,server FROM "' + db_name + '"')

    res = []
    for i in cur:
        res.append(i)
    cur.close()
    return res


def insert_number(num: int, name: str, client, server, db_name: str):
    cur = get_cursor()
    cur.execute(u'INSERT INTO "' + db_name + '" (number, name, client, server) VALUES (' + str(num)
                + ', \'' + name
                + '\', \'' + client
                + '\', \'' + server
                + '\')')
    cur.close()
    conn.commit()
    return 1


def reset(db_name: str):
    cur = get_cursor()

    cur.execute(u'DELETE FROM "' + db_name + '"')

    cur.close()
    conn.commit()

    return 1
