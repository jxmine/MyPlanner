from tasks import DATABASE
from flask import g
import sqlite3

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
        #gets the database
    return db
    #gets database 
