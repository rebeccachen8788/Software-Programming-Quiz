# Source: https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# Accessed 2/2/24

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from .db_connector import get_db_connection, execute_query
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Email, EqualTo, Length

bp = Blueprint('auth', __name__, url_prefix='/')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
    
class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=50, message=f"Password must be 8-50 characters long")])
    password2 = PasswordField('Confirm password', validators=[InputRequired(), EqualTo('password', message="Passwords must match")])
    firstName = StringField('First Name', validators=[InputRequired()])
    lastName = StringField('Last Name', validators=[InputRequired()])
    submit = SubmitField('Sign Up')
    
# User sign up
@bp.route('/signup', methods=['GET', 'POST'])
def signup():   
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fn = request.form['firstName']
        ln = request.form['lastName']
        error = None
        
        query = "INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES (%s, %s, %s, %s);"
        
        # attempt to insert the new user into the database
        if not error: 
            try:
                secure_password = generate_password_hash(password) 
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
    return render_template('/login-signup.html', loginForm=LoginForm(), signupForm=SignupForm())
        
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
    return render_template('/login-signup.html', loginForm=LoginForm(), signupForm=SignupForm())

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
