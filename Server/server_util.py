from flask import render_template
import util

def home(db, my_name):
    servers = []
    total = 0
    numbers = db.get_numbers(my_name)
    servers.append({"data": str(numbers)})
    total += sum([x[0] for x in numbers])
    return render_template("server.html", servers=servers, total=total % util.get_prime())