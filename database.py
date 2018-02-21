import util
import os
import psycopg2 as psy
testing = False
if str(os.path.dirname(__file__).split("/")[-1]) != "flaskwebsite":
    testing = True

if not testing:
    conn = psy.connect(host='localhost', user='bachelor', password='gruppen1234', dbname='bachelorprojekt')

    def get_conn():
        global conn
        conn = psy.connect(host='localhost', user='bachelor', passwd='gruppen1234', dbname='bachelorprojekt')


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

        cur.execute(u'select number,name from "' + db_name + '"')

        res = []
        for i in cur:
            res.append(i)
        cur.close()
        return res

    def insert_number(num: int, name: str, db_name: str):
        cur = get_cursor()
        cur.execute(u'insert into "' + db_name + '" (number, name) values (' + str(num) + ', \'' + name + '\')')
        cur.close()
        conn.commit()
        return 1

    def reset(db_name: str):
        cur = get_cursor()

        cur.execute(u'delete from "' + db_name + '"')

        cur.close()
        conn.commit()

        return 1

else:
    db = []
    db_names = []
    db_total = []

    def get_numbers(_: str):
        ret = []
        for num, i in enumerate(db):
            ret.append((i, db_names[num]))
        return db_total

    def insert_number(num, name, id: str):
        db.append(num)
        db_names.append(name)
        db_total.append((num, name))
        return 1

    def reset(_: str):
        global db, db_names, db_total
        db = []
        db_names = []
        db_total = []
        return 1




