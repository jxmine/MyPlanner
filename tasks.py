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
    sql = """
    SELECT Class.class, Task_List.task, To_Do_List.description, To_Do_List.due_date FROM To_Do_List 
    JOIN Task_List ON To_Do_List.task_id = Task_List.id
    JOIN Class ON To_Do_List.class_id = Class.id"""
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("task_list.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)