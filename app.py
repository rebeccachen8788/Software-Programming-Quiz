from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
import database.db_connector as db
import os

app = Flask(__name__)

db_connection = db.connect_to_database()
db_connection.ping(True)

app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_UserName'
app.config['MYSQL_PASSWORD'] = 'xxxx' #last 4 of onid
app.config['MYSQL_DB'] = 'cs340_UserName'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"


mysql = MySQL(app)


# Routes
@app.route('/')
def root():
    return "Welcome to the Capstone of Doom!"


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 12118))
    app.run(port=port, debug=True)