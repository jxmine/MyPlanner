from sqlite3.dbapi2 import Cursor
from flask import Flask, g, render_template, request, redirect, session, url_for, flash
from flask_login.utils import login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, UserMixin
import sqlite3
#importing all the things needed to run the website

class User(UserMixin):
    def __init__(self, id, username, password):
        self.username = username
        self.password = password
        self.id = id

# class User:
#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password
    
#     def __repr__(self):
#         return f'<User: {self.username}>'
#         #shows the user's username instead of showing their id 

# users = []
# users.append(User(id=0, username = 'jasmine', password = 'hungry'))
# users.append(User(id=1, username = 'hanan', password = 'test'))
#adds intances of user classes

app = Flask(__name__)
login_manager = LoginManager(app)
DATABASE = 'todolist.db'
app.secret_key = "jasmine"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        #gets the database
    return db
    #gets database

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT id, username, password FROM User WHERE id = ?', (user_id, )).fetchone()
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
def home():
    return render_template("home.html")
    #if the user is logged in, redirects the user to home
 
@app.route("/Task_List")
@login_required
def contents():
    cursor = sqlite3.connect(DATABASE).cursor()
    sql = """
    SELECT To_Do_List.id, Class.class, Task_List.task, To_Do_List.description, To_Do_List.due_date FROM To_Do_List 
    JOIN Task_List ON To_Do_List.task_id = Task_List.id
    JOIN Class ON To_Do_List.class_id = Class.id"""
    #gets all the data from the database and show them as what they are instead of their ids
    cursor.execute(sql)
    results = cursor.fetchall()

    return render_template("task_list.html", results=results)


@app.route("/edit")
@login_required
def edit():
    return render_template("edit.html")


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    db = get_db()
    cursor = db.cursor()
    for id in request.form.getlist('delete'):
        cursor.execute("DELETE FROM To_Do_List WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("contents"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        # session.pop("user_id", None)
        username = request.form["username"]
        password = request.form["password"]

        if username == "" or password == "":
            flash("Please enter a username and a password")
            return redirect(url_for("login"))

        if request.form.get('register'):
            db.execute('INSERT INTO User (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
            db.commit()
            flash("You are now registered!")
        user = db.execute('SELECT id, username, password FROM User WHERE username = ?', (username, )).fetchone()
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1], user[2]))
            flash("You are logged in!")
            return redirect(url_for("home"))


        # if request.form.get("register"):
        #     user = User(len(users), username, password)
        #     users.append(user)
        #     session["user_id"] = user.id
        # user = None

        # for user in users:
        #     if user.username == username and user.password == password:
        #         session['user_id'] = user.id
        #         return redirect(url_for("home"))
        #         #if the username and password is correct redirects to home

        flash("Failed to login :(")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    #removes the user from the session
    return redirect(url_for('login'))


@app.route("/add", methods=["POST"])
@login_required
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


if __name__ == "__main__":
    app.run(debug=True)