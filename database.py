try:
    import MySQLdb as mdb
    testing = False
except:
    testing = True


if not testing:
    conn = mdb.connect(host='localhost', user='bachelor', passwd='gruppen1234', db='bachelorprojekt', use_unicode=True, charset='utf8', init_command='SET NAMES UTF8')

    def get_conn():
        global conn
        conn = mdb.connect(host='localhost', user='bachelor', passwd='gruppen1234', db='bachelorprojekt', use_unicode=True, charset='utf8', init_command='SET NAMES UTF8')


    def get_cursor():
        global conn
        try:
            cursor = conn.cursor()
            cursor.execute("select 1;")
        except mdb.OperationalError:
            get_conn()
            cursor = conn.cursor()
        return cursor

    def get_numbers():
        cur = get_cursor()

        affected_count = cur.execute(u'select number from numbers')

        res = []
        for i in cur:
            res.append(i)

        cur.close()
        return res

    def add_number(num: int, name: str):
        cur = get_cursor()
        affected_count = cur.execute(u'insert into numbers (number, name) values (' + str(num) + ', "' + name + '")')
        cur.close()
        conn.commit()
        return int(affected_count > 0)

    def reset():
        cur = get_cursor()

        affected_count = cur.execute(u'delete from numbers')

        cur.close()
        conn.commit()

        return 1

else:
    db = []
    db_names = []

    def get_numbers():
        print("in here")
        return db

    def add_number(num, name):
        db.append(num)
        db_names.append(name)
        return 1

    def reset():
        global db
        db = []
        db_names = []
        return 1




