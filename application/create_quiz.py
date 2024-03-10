# Adapted from https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/ with the help of chatGPT

from flask import flash, get_flashed_messages, Blueprint, render_template, redirect, session, url_for, request
from flask_wtf import FlaskForm, Form
from wtforms import BooleanField, FieldList, FormField, IntegerField, RadioField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Length
from wtforms.widgets import NumberInput

from .db_connector import get_db_connection
from .auth import login_required


bp = Blueprint('create_quiz', __name__, url_prefix='/')

class QuestionForm(Form):
    # subform - QuizForm contains a list of QuestionForms
    questionText = StringField('questionText' , validators=[Length(max=500), InputRequired()], description="Question: ")
    questionType = SelectField('questionType', description='Question', choices=[('freeform', 'Freeform'), ('true-false', 'True/False'), ('multiple-choice', 'Multiple Choice'), ('check-all', 'Check All')])
    correctCheckboxes = FieldList(BooleanField('correctCheckboxes'), min_entries=1) # for check-all questions
    correctMultipleChoice = RadioField('correctMultipleChoice', choices=[('answer1', 'Answer 1'), ('answer2', 'Answer 2'), ('answer3', 'Answer 3'), ('answer4', 'Answer 4')])
    correctTrueFalse = RadioField('correctTrueFalse', choices=[('True', 'True'), ('False', 'False')])
    answers = FieldList(StringField('answer'), validators=[InputRequired(), Length(max=500)], min_entries=4, max_entries=4) 
    
class QuizForm(FlaskForm):
    # Parent form
    quizName = StringField('Quiz Name', validators=[InputRequired(), Length(max=200)], description="Name your quiz")
    timer = IntegerField('Time Limit', description="minutes", widget=NumberInput(min=5, max=180), validators=[InputRequired()])
    questions = FieldList(FormField(QuestionForm))
    submit = SubmitField('Create Quiz')
 
@bp.route('/create_quiz', methods=['GET', 'POST'])
@login_required # prevents unauthenticated users from accessing this page
def create_quiz():
    form = QuizForm(request.form)
    creatorID = session['user_id']
    
    if form.validate_on_submit():
        # create new quiz in database
        try:
            db = get_db_connection()
            cursor = db.cursor()
            
            # create new quiz entry for user
            cursor.execute("INSERT INTO Quiz (creatorID, title, time) VALUES (%s, %s, %s)", (creatorID, form.quizName.data, form.timer.data))
            
            # retrieve the quizID
            cursor.execute("SELECT LAST_INSERT_ID()")
            quiz_id = cursor.fetchone()[0]

            seen_questions = set()
            # Loop over each question in the form and insert into the database
            for key, value in request.form.items():
                if key.startswith('subform-'):
                    # Extract question number from the key
                    question_number = key.split('-')[1]
                    if question_number in seen_questions:
                        continue
                    seen_questions.add(question_number)
                    
                    # Extract question text and type
                    question_text = request.form[f'subform-{question_number}-questionText']
                    question_type = request.form[f'subform-{question_number}-questionType']
                    
                    # Extract correct answers
                    correct_answers = []
                    if question_type == "check-all":
                        correct_answers = request.form.getlist(f'subform-{question_number}-correctCheckbox')
                                                                       
                    elif question_type == "multiple-choice" or question_type == "true-false":
                        correct_answers = request.form.get(f'subform-{question_number}-correctRadio')
                    
                    # Extract all answers
                    all_answers = []
                    if question_type == "true-false":
                        all_answers.append(["True", "True" in correct_answers])
                        all_answers.append(["False", "False" in correct_answers])
                    
                    elif question_type != "freeform": 
                        for option in ['answer1', 'answer2', 'answer3', 'answer4']:
                            answer = request.form.get(f'subform-{question_number}-{option}')
                            if answer: 
                                all_answers.append([answer, option in correct_answers])
                    
                    # Insert question into database and retrieve questionID
                    cursor.execute("INSERT INTO Question (quizID, type, details, score) VALUES (%s, %s, %s, %s)", (quiz_id, question_type, question_text, 1))
                    if question_type != "freeform":
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        question_id = cursor.fetchone()[0]
                        
                        # insert answers into database
                        for answer in all_answers:
                            cursor.execute("INSERT INTO Answers (questionID, details, correct) VALUES (%s, %s, %s)", (question_id, answer[0], answer[1]))                        

            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('creator_homepage.creator_homepage'))
        except Exception as e:
            flash(('An error occurred while processing your request.', 'danger'))
            return redirect(url_for('create_quiz.create_quiz'))
    else: 
        # handle form validation errors as flash message
        for field, errors in form.errors.items():
            for error in errors:
                flash((error, 'warning'))
            
    return render_template('create_quiz.html', form=form)
