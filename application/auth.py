# Source: https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# Accessed 2/2/24

import flask_login
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from .db_connector import get_db_connection, execute_query

bp = Blueprint('auth', __name__, url_prefix='/')



# User registration
@bp.route('/login', methods=['GET', 'POST'])
def register():
    
    # db test
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Quiz_Creator;")
    for i in cursor:
        print(i)
    cursor.close()    
    
    
    
    # if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']
    #     fn = request.form['firstName']
    #     ln = request.form['lastName']
    #     error = None
        
    #     # form validation
    #     if not email:
    #         error = 'Email is required.'
    #     elif not password:
    #         error = 'Password is required.'
    #     # WIP -> elif other password requirements
    #     else:
    #         password = generate_password_hash(password)
    #         query = "INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES {%s, %s, %s, %s};"
        
    #     # attempt to insert the new user into the database
    #     if not error: 
    #         try:
    #             cursor = execute_query(db_connection=None, query=query, query_params=(email, password, fn, ln))
    #             user = cursor.fetchall()

                
    #         except not user:
    #             error = "Email already exists. Please use the login form."
    #         else:
    #             query = "SELECT creatorID FROM Quiz_Creator WHERE creatorEmail={%s};"
    #             session.clear()
    #             # cursor = execute_query(db)
    #             # session['user_id'] = 
    #             return redirect(url_for("home"))
    #     flash(error)
    #     print()
    return render_template('/login.html')
        
# # User login
# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         db = connect_to_database
#         error = None
#         query = "SELECT * FROM Quiz_Creator WHERE creatorEmail = '{%s}';"
#         user = db.execute(query, (email))
        
#         # validate username and password combo
#         if not user:
#             error = "No existing accounts with this email address."
#         elif not check_password_hash(user['password'], password):
#             error = "Incorrect password."
        
#         if error is None:
#             session.clear()
#             session['user_id'] = user['creatorID']
#             return redirect(url_for('home'))

#         flash(error)      
    
#     return render_template('/login.html')

