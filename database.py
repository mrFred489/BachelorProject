import MySQLdb as mdb

conn = mdb.connect(host='localhost', user='bachelor', passwd='gruppen1234', db='bachelorprojekt', use_unicode=True, charset='utf8', init_command='SET NAMES UTF8')


def get_conn():
    global conn
    conn = mdb.connect(host='localhost', user='shoppinglist', passwd='shop', db='shoppinglists', use_unicode=True, charset='utf8', init_command='SET NAMES UTF8')


def get_cursor():
    global conn
    try:
        cursor = conn.cursor()
        cursor.execute("select 1;")
    except mdb.OperationalError:
        get_conn()
        cursor = conn.cursor()
    return cursor




