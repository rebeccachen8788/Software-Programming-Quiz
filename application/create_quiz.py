# Adapted from https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/ with the help of chatGPT

from flask import flash, Blueprint, render_template, redirect, session, url_for, request
from flask_wtf import FlaskForm, Form
from wtforms import BooleanField, FieldList, FormField, IntegerField, RadioField, StringField
from wtforms import validators
from wtforms.widgets import NumberInput

from .db_connector import get_db_connection
from .auth import login_required


bp = Blueprint('create_quiz', __name__, url_prefix='/')

class QuestionForm(Form):
    # subform - QuizForm contains a list of QuestionForms
    questionText = StringField('questionText' , [validators.Length(min=1, max=500)], description="Question: ")
    questionType = StringField('questionType')
    correctCheckboxes = FieldList(BooleanField('correctCheckboxes')) # for check all questions
    correctRadio = RadioField('correctRadio') # for true/false and multiple choice questions
    answers = FieldList(StringField('answer'))
    
class QuizForm(FlaskForm):
    # Parent form - will need to implement timer, and anything else we need for the quiz
    timer = IntegerField('Time Limit', description="minutes", widget=NumberInput(min=5, max=180))
    questions = FieldList(FormField(QuestionForm))
 
@bp.route('/create_quiz', methods=['GET', 'POST'])
@login_required # prevents unauthenticated users from accessing this page
def create_quiz():
    form = QuizForm(request.form)

    creatorID = session.get('user_id')  
    # session data is used to store the current quiz being created
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
            print(e)
            flash('An error occurred while creating the quiz. Please try again.')
            return render_template('homepage.html')
            
    if form.validate_on_submit():
        # form validation by Flask-WTF
        try: 
            db = get_db_connection()
            cursor = db.cursor()
            # set time limit for quiz
            query = "UPDATE Quiz SET time = %s WHERE quizID = %s"
            cursor.execute(query, (form.timer.data, session['quiz_id']))
            seen_questions = set()
            print(form.questions)
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
                    if question_type == "check-all":
                        correct_answers = request.form.getlist(f'subform-{question_number}-correctCheckboxes')
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
                    cursor.execute("INSERT INTO Question (quizID, type, details, score) VALUES (%s, %s, %s, %s)", (session['quiz_id'], question_type, question_text, 1))
                    if question_type != "freeform":
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        question_id = cursor.fetchone()[0]
                        
                        # insert answers into database
                        for answer in all_answers:
                            cursor.execute("INSERT INTO Answers (questionID, details, correct) VALUES (%s, %s, %s)", (question_id, answer[0], answer[1]))                        

            db.commit()
            cursor.close()
            db.close()
            print('Quiz created successfully!')
            # remove quizID from session
            session.pop('quiz_id', None)
            return redirect(url_for('root'))
        except Exception as e:
            print(e)
            flash('An error occurred while creating the quiz. Please try again.')
            return redirect(url_for('create_quiz.create_quiz'))
    return render_template('create_quiz.html', form=form)
