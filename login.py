from sqlite3.dbapi2 import Cursor
from flask import Flask, g, render_template, request, redirect, session, url_for
import sqlite3

from flask.helpers import flash
#importing all the things needed to run the website

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f'<User: {self.username}>'
        #shows the user's username instead of showing their id 

users = []
users.append(User(id=0, username = 'jasmine', password = 'hungry'))
users.append(User(id=1, username = 'hanan', password = 'test'))
#adds intances of user classes

app = Flask(__name__)
DATABASE = 'todolist.db'
app.secret_key = "jasmine"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        #gets the database
    return db
    #gets database

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
        #if the user isn't logged in, redirects them to the login page

    return render_template("home.html")
    #if the user is logged in, redirects the user to home

 
@app.route("/Task_List")
def contents():
    cursor = sqlite3.connect(DATABASE).cursor()
    sql = """
    SELECT To_Do_List.id, Class.class, Task_List.task, To_Do_List.description, To_Do_List.due_date FROM To_Do_List 
    JOIN Task_List ON To_Do_List.task_id = Task_List.id
    JOIN Class ON To_Do_List.class_id = Class.id"""
    #gets all the data from the database and show them as what they are instead of their ids
    cursor.execute(sql)
    results = cursor.fetchall()
    if not g.user:
        return redirect(url_for("login"))

    return render_template("task_list.html", results=results)


@app.route("/edit")
def edit():
    if not g.user:
        return redirect(url_for("login"))

    return render_template("edit.html")

@app.route("/delete", methods=["POST"])
def delete():
    if not g.user:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    for id in request.form.getlist('delete'):
        cursor.execute("DELETE FROM To_Do_List WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("contents"))

@app.before_request
def before_request():
    g.user = None

    if "user_id" in session:
        for user in users:
            if user.id == session["user_id"]:
                g.user = user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.form.get("register"):
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        users = request.form["user"]
        user_id = cursor.execute("SELECT id FROM User WHERE username == ?", (users,)).fetchone()
        if user_id is None:
            cursor.execute("INSERT INTO User(username) VALUES (?)", (users,))
            user_id = cursor.execute("SELECT id FROM User WHERE username == ?", (users,)).fetchone()
        user_id = user_id[0]

        passwords = request.form["password"]
        password = cursor.execute("SELECT id FROM User WHERE password == ?", (passwords,)).fetchone()
        if password is None:
            cursor.execute("INSERT INTO User(password) VALUES (?)", (passwords,))
            password = cursor.execute("SELECT id FROM User WHERE password == ?", (passwords,)).fetchone()
        password = password[0]
        sql = "INSERT INTO User(user, password) VALUES (?, ?)"
        cursor.execute(sql, (user_id, password))
        db.commit()
        
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    #removes the user from the session
    return redirect(url_for('login'))

@app.route("/add", methods=["POST"])
def add_task():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    klass = request.form["class"]
    if len(klass) > 20:
        return redirect("/edit")
    klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    if klass_id is None:
        cursor.execute("INSERT INTO Class(class) VALUES (?)", (klass,))
        klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    klass_id = klass_id[0]

    task = request.form["task"]
    if len(task) > 20:
        return redirect("/edit")
    task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    if task_id is None:
        cursor.execute("INSERT INTO Task_List(task) VALUES (?)", (task,))
        task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    task_id = task_id[0]

    description = request.form["description"]
    if len(description) > 20:
        return redirect("/edit")
    new_due_date = request.form["due_date"]
    if len(new_due_date) > 20:
        return redirect("/edit")
    sql = "INSERT INTO To_Do_List(class_id, task_id, description, due_date) VALUES (?, ?, ?, ?)"
    print(klass_id, type(klass_id))
    cursor.execute(sql, (klass_id, task_id, description, new_due_date))
    #gets the data from the database and puts each of the different data into different tables
    db.commit()
    return redirect("/Task_List")


"""@app.route("/delete")
def delete():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    db.commit()"""


if __name__ == "__main__":
    app.run(debug=True)