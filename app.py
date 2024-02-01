# from flask import Flask, render_template, json, redirect
# from flask_mysqldb import MySQL
# from flask import request
# import database.db_connector as db
# import os
#
# app = Flask(__name__)
#
# db_connection = db.connect_to_database()
# db_connection.ping(True)
#
#
# mysql = MySQL(app)
#
#
# # Routes
# @app.route('/')
# def root():
#     return "Welcome to the Capstone of Doom!"
#
#
# # Listener
# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 12118))
#     app.run(port=port, debug=True)

from flask import Flask, render_template
import os
from database.db_connector import get_db_connection

app = Flask(__name__)
db_connection = get_db_connection()
db_connection.ping(True)

@app.route('/')
def root():
    return render_template("homepage.html")


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 12118))
    app.run(port=port, debug=True)
