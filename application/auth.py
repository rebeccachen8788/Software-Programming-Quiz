# Source: https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# Accessed 2/2/24

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from .db_connector import get_db_connection
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Email, EqualTo, Length

bp = Blueprint('auth', __name__, url_prefix='/')

class LoginForm(FlaskForm):
    email = EmailField('Email', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    submit = SubmitField('Login')
    
class SignupForm(FlaskForm):
    email = EmailField('Email', [InputRequired(), Email(message="Invalid email address.")], description="Email address must be valid.")
    password = PasswordField('Password', [InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters long"), EqualTo('password2', message="Passwords must match")])
    password2 = PasswordField('Confirm password', [InputRequired()])
    firstName = StringField('First Name', [InputRequired()])
    lastName = StringField('Last Name', [InputRequired()])
    submit = SubmitField('Sign Up')
    
# User sign up
@bp.route('/signup', methods=['GET', 'POST'])
def signup(flashMessage = None):
    # display flash message if there is one
    if flashMessage:
        flash(flashMessage, "\n")
        
    signupForm = SignupForm()
    loginForm = LoginForm()

    # if the form is submitted, validate the data and insert the new user into the database
    if signupForm.validate_on_submit():
        email = signupForm.email.data
        password = signupForm.password.data
        fn = signupForm.firstName.data
        ln = signupForm.lastName.data
        query = "INSERT INTO Quiz_Creator (creatorEmail, password, firstName, lastName) VALUES (%s, %s, %s, %s);"
        # attempt to insert the new user into the database
        try:
            secure_password = generate_password_hash(password) 
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query, (email, secure_password, fn, ln))
            db.commit()
            flashMessage = "Signup Successful! Please log in to access your account."          
        except Exception as e:
            if 'Duplicate entry' in str(e):
                flashMessage = "Email already in use. Please log in or use a different email address."
            else:
                flashMessage = e
        finally:
            cursor.close()
            db.close()
            if flashMessage:
                flash(flashMessage)
            return redirect(url_for('auth.login'))    
    
    else:
        # handle form validation errors as flash message for consistency
        for field, errors in signupForm.errors.items():
            for error in errors:
                flashMessage = f"{error}"
                flash(flashMessage)      
    return render_template('/login-signup.html', loginForm=loginForm, signupForm=signupForm)
      
# User login
@bp.route('/login', methods=['GET', 'POST'])
def login(flashMessage = None):
    # display flash message if there is one
    if flashMessage:
        flash(flashMessage)
        
    signupForm = SignupForm()
    loginForm = LoginForm()
    
    # if the form is submitted with valid data, check the database for the user
    if loginForm.validate_on_submit():
        email = loginForm.email.data
        password = loginForm.password.data
        try: 
            query = "SELECT creatorID, firstName, password FROM Quiz_Creator WHERE creatorEmail = %s;"
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, (email,)) 
            user = cursor.fetchone()
            cursor.close()
            db.close()
        except Exception as e:
            flashMessage = e
        else:
            # if user not found, flash message
            if not user:
                flashMessage = "Email not found. Please sign up for an account."
            # if email exists, check if password is valid
            elif check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['creatorID']
                session['user_name'] = user['firstName']
                return redirect(url_for('root'))
            else:
                flashMessage = "Incorrect password. Please try again."
        finally:
            if flashMessage:
                flash(flashMessage)
    return render_template('/login-signup.html', loginForm=loginForm, signupForm=signupForm)

# logout
@bp.route('/logout')
def logout():
    session.clear()
    print("session cleared")
    # return to login page and display successful logout message
    return login(flashMessage="You have been logged out.")

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
            return signup(flashMessage="Please login or signup to access your account.")
        return view(**kwargs)
    
    return wrapped_view
