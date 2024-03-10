from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo, Length, ValidationError
from flask import Blueprint, render_template, flash, session, get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from .db_connector import get_db_connection
from .auth import login_required
bp = Blueprint('settings', __name__)

def password():
    def _password(form, field):
        user_id = session['user_id']
        query = "SELECT password FROM Quiz_Creator WHERE creatorID = %s;"
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if not result:
                print('no password?')
                raise ValidationError('There was an issue retrieving your password. Please try again.')
            else:
                storedPassword = result[0]
                if not check_password_hash(storedPassword, field.data):
                    raise ValidationError('The password you entered is incorrect. Please try again.')
        except Exception as e:
            print(e)
            raise ValidationError(e)
        finally:
            cursor.close()
            db.close()
    return _password

# change password
class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', [InputRequired(), password()])
    newPassword = PasswordField('New Password', [InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters long"), EqualTo('newPassword2', message="Passwords must match")])
    newPassword2 = PasswordField('Confirm New Password', [InputRequired()])
    submit = SubmitField('Update Password')
    
# change name
class ChangeNameForm(FlaskForm):
    password = PasswordField('Password', [InputRequired(), password()])
    firstName = StringField('First Name', [InputRequired()])
    lastName = StringField('Last Name', [InputRequired()])
    submit = SubmitField('Update Name')
    
# delete account
class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', [InputRequired(), password()])
    confirmation = StringField('Type "DELETE" to confirm you want to delete your account', [InputRequired()], \
        description="Deleting your account will permanently remove all quiz records.")
    def validate_confirmation(form, field):
        if field.data != 'DELETE':
            raise ValidationError('Please type "DELETE" to confirm account deletion.')
    submit = SubmitField('Delete Account')
    
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    changePasswordForm = ChangePasswordForm()
    changeNameForm = ChangeNameForm()
    deleteAccountForm = DeleteAccountForm()
    
    return render_template('settings.html', changePasswordForm=changePasswordForm, changeNameForm=changeNameForm, deleteAccountForm=deleteAccountForm, messages=get_flashed_messages())  

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        newPassword = form.newPassword.data
        user_id = session['user_id']
        query = "UPDATE Quiz_Creator SET password = %s WHERE creatorID = %s;"
        try:
            secure_password = generate_password_hash(newPassword)
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query, (secure_password, user_id))
            db.commit()
            print("success!")
            flash(("Password updated successfully!", 'success'))
        except Exception as e:
            flash((e, 'danger'))
        finally:
            cursor.close()
            db.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash((error, 'warning'))
    changeNameForm = ChangeNameForm()
    deleteAccountForm = DeleteAccountForm()
    return render_template('settings.html', changePasswordForm=form, changeNameForm=changeNameForm, deleteAccountForm=deleteAccountForm, messages=get_flashed_messages())

@bp.route('/change_name', methods=['POST'])
@login_required
def change_name():
    form = ChangeNameForm()   
    if form.validate_on_submit():
        firstName = form.firstName.data
        lastName = form.lastName.data
        user_id = session['user_id']
        query = "UPDATE Quiz_Creator SET firstName = %s, lastName = %s WHERE creatorID = %s;"
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query, (firstName, lastName, user_id))
            db.commit()
            session['user_name'] = firstName
            session['user_last_name'] = lastName
            flash(("Name updated successfully!", 'success'))
        except Exception as e:
            flash((e, 'danger'))
        finally:
            cursor.close()
            db.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash((error, 'warning'))
    changePasswordForm = ChangePasswordForm()
    deleteAccountForm = DeleteAccountForm()
    return render_template('settings.html', changePasswordForm=changePasswordForm, changeNameForm=form, deleteAccountForm=deleteAccountForm, messages=get_flashed_messages())

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        query = "DELETE FROM Quiz_Creator WHERE creatorID = %s;"
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            db.commit()
            session.clear()
            flash(("Your account has been deleted.", 'success'))
            return render_template('deleted_account.html', messages=get_flashed_messages())
        except Exception as e:
            flash((e, 'danger'))
        finally:
            cursor.close()
            db.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash((error, 'warning'))
    changePasswordForm = ChangePasswordForm()
    changeNameForm = ChangeNameForm()
    return render_template('settings.html', changePasswordForm=changePasswordForm, changeNameForm=changeNameForm, deleteAccountForm=form, messages=get_flashed_messages())    
