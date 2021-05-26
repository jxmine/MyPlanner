from sqlite3.dbapi2 import Cursor
from flask import Flask, g, render_template, request, redirect, session, url_for
import sqlite3

from flask.helpers import flash

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username = 'jasmine', password = 'hungry'))
users.append(User(id=2, username = 'hanan', password = 'test'))

app = Flask(__name__)
DATABASE = 'todolist.db'
app.secret_key = "jasmine"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
    return db
#get database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
#close connection
@app.route("/")
def home():
    if not g.user:
        return redirect(url_for("login"))

    return render_template("home.html")

 
@app.route("/Task_List")
def contents():
    cursor = sqlite3.connect(DATABASE).cursor()
    sql = """
    SELECT Class.class, Task_List.task, To_Do_List.description, To_Do_List.due_date FROM To_Do_List 
    JOIN Task_List ON To_Do_List.task_id = Task_List.id
    JOIN Class ON To_Do_List.class_id = Class.id"""
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("task_list.html", results=results)


@app.route("/edit")
def edit():
    return render_template("edit.html")

@app.before_request
def before_request():
    g.user = None

    if "user_id" in session:
        for user in users:
            if user.id == session["user_id"]:
                g.user = user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("user_id", None)

        username = request.form["username"]
        password = request.form["password"]

        # user = None
        for user in users:
            if user.username == username and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for("home"))

        flash("Failed to login")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/add", methods=["POST"])
def add_task():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    klass = request.form["class"]
    klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    if klass_id is None:
        cursor.execute("INSERT INTO Class(class) VALUES (?)", (klass,))
        klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    klass_id = klass_id[0]

    task = request.form["task"]
    task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    if task_id is None:
        cursor.execute("INSERT INTO Task_List(task) VALUES (?)", (task,))
        task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    task_id = task_id[0]

    description = request.form["description"]
    new_due_date = request.form["due_date"]
    sql = "INSERT INTO To_Do_List(class_id, task_id, description, due_date) VALUES (?, ?, ?, ?)"
    print(klass_id, type(klass_id))
    cursor.execute(sql, (klass_id, task_id, description, new_due_date))
    db.commit()
    return redirect("/Task_List")


if __name__ == "__main__":
    app.run(debug=True)