# Source: https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# Accessed 2/2/24

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from .db_connector import get_db_connection, execute_query

bp = Blueprint('auth', __name__, url_prefix='/')



# User sign up
@bp.route('/signup', methods=['GET', 'POST'])
def signup():   
    
    if request.method == 'POST':
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        fn = request.form['firstName']
        ln = request.form['lastName']
        error = None
        
        # form validation
        if not email:
            error = 'Signup Error: Email is required.'
        elif not password1:
            error = 'Signup Error: Password is required.'
        elif password1 != password2:
            error = 'Signup Error: Passwords do not match.'
        elif len(password1) < 8:
            error = "Signup Error: Password must be at least 8 characters long."
            print(error)
        # WIP -> elif other password requirements
        else:
            query = "INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES (%s, %s, %s, %s);"
        
        # attempt to insert the new user into the database
        if not error: 
            try:
                secure_password = generate_password_hash(password1) 
                db = get_db_connection()
                user = execute_query(db, query, (email, secure_password, fn, ln)) 
            except not user:
                error = "Signup Error: An account with this email already exists."
            else:
                info = "Signup Successful: Please log in to your account."
                flash(info)
                return redirect(url_for('root'))
            finally:
                db.close()
        flash(error)
    return render_template('/login-signup.html')
        
# User login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        query = "SELECT creatorID, password FROM Quiz_Creator WHERE creatorEmail = %s;"
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (email,)) 
        # validate username and password combo
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            if check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['creatorID']
                return redirect(url_for('root'))
            else:
                error = "Incorrect password."
        else: 
            error = "Email not found."
        flash(error)      
    return render_template('/login-signup.html')

# logout
@bp.route('/logout')
def logout():
    session.clear()
    print("session cleared")
    return redirect(url_for('auth.login'))

# checks if a user id is stored in the session
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if not user_id:
        g.user = None
    else:
        query = 'SELECT * FROM Quiz_Creator WHERE creatorID = %s'
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        g.user = cursor.fetchone()
        cursor.close()
        db.close()

# redirects to login/signup page if user is not authenticated when @login_required decorator used
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('auth.signup'))
        return view(**kwargs)
    
    return wrapped_view
