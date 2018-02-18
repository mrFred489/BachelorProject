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

    def get_numbers(db_name):
        cur = get_cursor()

        affected_count = cur.execute(u'select number from `' + db_name + '`')

        res = []
        for i in cur:
            res.append(i[0])

        cur.close()
        return res

    def add_number(num: int, name: str, db_name: str):
        cur = get_cursor()
        affected_count = cur.execute(u'insert into `' + db_name + '` (number, name) values (' + str(num) + ', "' + name + '")')
        cur.close()
        conn.commit()
        return int(affected_count > 0)

    def reset(db_name: str):
        cur = get_cursor()

        affected_count = cur.execute(u'delete from `' + db_name + '`')

        cur.close()
        conn.commit()

        return 1

else:
    db = []
    db_names = []

    def get_numbers(_: str):
        return db

    def add_number(num, name, _: str):
        db.append(num)
        db_names.append(name)
        return 1

    def reset(_: str):
        global db
        db = []
        db_names = []
        return 1




