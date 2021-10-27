from sqlite3.dbapi2 import Cursor
from flask import Flask, g, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, UserMixin, current_user
import sqlite3
#importing all the things needed to run the website

class User(UserMixin):
    def __init__(self, id, username, password):
        self.username = username
        self.password = password
        self.id = id

app = Flask(__name__)
login_manager = LoginManager(app)
DATABASE = 'todolist.db'
app.secret_key = "jasmine"

@login_manager.unauthorized_handler
#redirects unauthorized users back to login
def unauthorized_callback():
    return redirect('/login')

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        #gets the database
    return db

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT id, username, password FROM User WHERE id = ?', (user_id, )).fetchone()
    #finds the user in the database
    if user:
        return User(user[0], user[1], user[2])

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
    #close connection


@app.route("/")
@login_required
#page only be shown if user is logged in
def home():
    return render_template("home.html")
    #redirects the user to home
 
@app.route("/Task_List")
@login_required
def contents():
    cursor = sqlite3.connect(DATABASE).cursor()
    sql = """
    SELECT To_Do_List.id, Class.class, Task_List.task, To_Do_List.description, To_Do_List.due_date FROM To_Do_List 
    JOIN Task_List ON To_Do_List.task_id = Task_List.id
    JOIN Class ON To_Do_List.class_id = Class.id WHERE To_Do_List.user_id = ?"""
    #gets all the data from the database and show them as what they are instead of their ids
    cursor.execute(sql, (current_user.id, ))
    results = cursor.fetchall()

    return render_template("task_list.html", results=results)


@app.route("/add")
@login_required
def add():
    return render_template("add.html")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    db = get_db()
    cursor = db.cursor()
    for id in request.form.getlist('delete'):
        cursor.execute("DELETE FROM To_Do_List WHERE id = ?", (id,))
        #delete the tasks in the to do list according to the selected ids
    db.commit()
    flash("The task/tasks has been deleted")
    return redirect(url_for("contents"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        username = request.form["username"]
        password = request.form["password"]
        user = db.execute('SELECT id, username, password FROM User WHERE username = ?', (username, )).fetchone()

        if username == "" or password == "":
            #user is redirected back to login if the required input values is blank 
            flash("Please enter a username and a password")
            return redirect(url_for("login"))

        if request.form.get('register'):
            sql = "SELECT username FROM User WHERE username = ?;"
            cursor = db.cursor()
            cursor.execute(sql, (username,))
            users = cursor.fetchone()
            # get all usernames in database and store them in users
            if users is not None:
            # if username taken, user would be redirected back to login
                flash("This username is already taken")
                return render_template("login.html")
            else:
                db.execute('INSERT INTO User (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
                #creates a password hash so the actual password won't be shown in the database           
                db.commit()
                flash("You are now registered!")

        if user and check_password_hash(user[2], password):
            #checks if the user is in the database
            #if so, logs user in
            login_user(User(user[0], user[1], user[2]))
            flash("You are logged in!")
            return redirect(url_for("home"))

        flash("Failed to login :(")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    #logs the user out
    flash("You are now logged out")
    return redirect(url_for('login'))


@app.route("/add", methods=["POST"])
@login_required
def add_task():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    klass = request.form["class"]
    if len(klass) > 20:
    #character limit
        return redirect("/add")
    klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    #finds the id of the class
    if klass_id is None:
        cursor.execute("INSERT INTO Class(class) VALUES (?)", (klass,))
        #if the class id is not found, add it to the database
        klass_id = cursor.execute("SELECT id FROM Class WHERE class == ?", (klass,)).fetchone()
    klass_id = klass_id[0]

    task = request.form["task"]
    if len(task) > 20:
        return redirect("/add")
    task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    if task_id is None:
        cursor.execute("INSERT INTO Task_List(task) VALUES (?)", (task,))
        task_id = cursor.execute("SELECT id FROM Task_List WHERE task == ?", (task,)).fetchone()
    task_id = task_id[0]

    description = request.form["description"]
    if len(description) > 30:
        return redirect("/add")
    new_due_date = request.form["due_date"]

    if len(new_due_date) > 20:
        return redirect("/add")
    sql = "INSERT INTO To_Do_List(class_id, task_id, description, due_date, user_id) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(sql, (klass_id, task_id, description, new_due_date, current_user.id))
    #gets the data from the database and puts each of the different data into different tables
    db.commit()
    return redirect("/Task_List")


if __name__ == "__main__":
    app.run(debug=True)