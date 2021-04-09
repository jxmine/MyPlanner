from flask import Flask, g, render_template
import sqlite3


app = Flask(__name__)
DATABASE = 'todolist.db'

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
    return render_template("home.html")



@app.route("/Task_List")
def contents():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Task_List"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("task_list.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)