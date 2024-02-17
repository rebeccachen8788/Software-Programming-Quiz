# Source: https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/

from flask import flash, Flask, Blueprint, render_template, redirect, session, url_for, request
from flask_wtf import FlaskForm
import random
from wtforms import Form, FieldList, FormField, IntegerField, SelectField, \
        StringField, TextAreaField, SubmitField
from wtforms import validators

from .db_connector import get_db_connection
from .auth import login_required


bp = Blueprint('create_quiz', __name__, url_prefix='/')

class QuestionForm(FlaskForm):
    questionText = StringField('Question', [validators.InputRequired()])
    questionType = SelectField('Question Type', choices=[
        ('true_false', 'True/False'),
        ('multiple_choice', 'Multiple Choice'),
        ('checkAll', 'Check All'),
        ('freeform', 'Freeform')
    ])
    correctAnswers = FieldList(StringField('Correct Answer'), min_entries=1)
    allAnswers = FieldList(StringField('Answer'), min_entries=2)    

class QuizForm(FlaskForm):
    questions = FieldList(FormField(QuestionForm), min_entries=1)
    
@bp.route('/create_quiz', methods=['GET', 'POST'])
# @login_required -> prevents unauthenticated users from accessing this page
def create_q():
    form = QuizForm(request.form)
    template_form = QuestionForm(prefix='subform')
    creatorID = session.get('user_id')  # Use get() to avoid KeyError if 'user_id' is not in session

    if 'quiz_id' not in session:
        try:
            db = get_db_connection()
            cursor = db.cursor()
            
            # create new quiz entry for user
            cursor.execute("INSERT INTO Quiz (creatorID, time) VALUES (%s, %s)", (creatorID, 0))
            db.commit()
            
            # retrieve the quizID
            cursor.execute("SELECT LAST_INSERT_ID()")
            quiz_id = cursor.fetchone()[0]
            
            # store quizID in session            
            session['quiz_id'] = quiz_id
            cursor.close()
            db.close()
        except Exception as e:
            flash('An error occurred while creating the quiz. Please try again.')
            return redirect(url_for('create_quiz.create_q'))
            
    if request.method == 'POST' and form.validate_on_submit():
        try: 
            db = get_db_connection()
            cursor = db.cursor()
            # Loop over each question in the form and insert into the database
            for question_form in form.questions:  # Access questions as a list of dictionaries
                question_text = question_form.questionText.data
                question_type = question_form.questionType.data
                correct_answers = []
                print(question_text, question_type)
                print("here? ", question_text, question_type)
                # Insert the question into the database and associate it with the quiz ID
                insert_query = "INSERT INTO Questions (text, question_type, quiz_id) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (question_text, question_type, session['quiz_id']))

            db.commit()
            cursor.close()
            db.close()
            flash('Quiz created successfully!')
            return redirect(url_for('create_quiz.create_q'))
        except Exception as e:
            flash('An error occurred while creating the quiz. Please try again.')
            return redirect(url_for('create_quiz.create_q'))
    return render_template('create_quiz.html', form=form)


@bp.route('/submit_question', methods=['POST'])
# @login_required -> prevents unauthenticated users from accessing this page
def submit_question():
    question_text = request.form.get('questionText')
    correct_answers = request.form.getlist('correctAnswer[]')
    answer1 = request.form.get('answer1')
    answer2 = request.form.get('answer2')
    answer3 = request.form.get('answer3')
    answer4 = request.form.get('answer4')

    if not correct_answers:
        # make this a pop up message for the user
        print("Please select correct answers")
        return redirect(url_for('create_quiz.create_q'))

    c_answers = []
    for val in correct_answers:
        if val == 'answer1':
            c_answers.append(answer1)
        elif val == 'answer2':
            c_answers.append(answer2)
        elif val == 'answer3':
            c_answers.append(answer3)
        elif val == 'answer4':
            c_answers.append(answer4)
        elif val == 'True':
            c_answers.append('True')
        elif val == 'False':
            c_answers.append('False')
    print("remade:", c_answers)
    # Here, you would save the question and correct answer to your database
    # For demonstration, let's just print them
    print(f"Question: {question_text}, Correct Answer: {correct_answers}, Answer1: {answer1}, Answer2: {answer2},"
          f"Answer3: {answer3}, Answer4: {answer4}")

    # Redirect to the quiz creation page or to a confirmation page
    return redirect(url_for('create_quiz.create_q'))