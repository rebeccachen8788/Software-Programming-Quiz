# Source: https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/

from flask import flash, Flask, Blueprint, render_template, redirect, session, url_for, request
from flask_wtf import FlaskForm
import random
from wtforms import BooleanField, Form, FieldList, FormField, IntegerField, RadioField, SelectMultipleField, \
    SelectField, StringField, TextAreaField, SubmitField
from wtforms import validators

from .db_connector import get_db_connection
from .auth import login_required


bp = Blueprint('create_quiz', __name__, url_prefix='/')

class QuestionForm(Form):
    questionText = StringField('questionText')
    questionType = StringField('questionType')
    correctCheckboxes = FieldList(BooleanField('answers'))
    correctRadio = RadioField('correctAnswer')
    answers = FieldList(StringField('answer'))
    
class QuizForm(FlaskForm):
    #timer = IntegerField('timer', [validators.NumberRange(min=1, max=120)])
    questions = FieldList(FormField(QuestionForm))
    
    # Override the form's populate_obj method to handle prefixed field names
    def populate_obj(self, obj):
        super().populate_obj(obj)
        for i, question in enumerate(obj.questions):
            prefix = f"subform-{i}-"
            for field_name, field_value in question.items():
                if hasattr(obj, field_name):
                    setattr(obj, field_name, field_value)
                else:
                    setattr(obj, f'{prefix}{field_name}', field_value)
                    
@bp.route('/create_quiz', methods=['GET', 'POST'])
@login_required # prevents unauthenticated users from accessing this page
def create_quiz():
    form = QuizForm(request.form)

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
            print(e)
            flash('An error occurred while creating the quiz. Please try again.')
            return render_template('homepage.html')
            
    if request.method == 'POST':
        if form.validate_on_submit():
            try: 
                db = get_db_connection()
                cursor = db.cursor()
                seen_questions = set()
                # Loop over each question in the form and insert into the database
                for key, value in request.form.items():
                    if key.startswith('subform-'):
                        # Extract question number from the key
                        question_number = key.split('-')[1]
                        if question_number in seen_questions:
                            continue
                        seen_questions.add(question_number)
                        
                        # Extract question text
                        question_text = request.form[f'subform-{question_number}-questionText']
                        
                        # Extract question type
                        question_type = request.form[f'subform-{question_number}-questionType']
                        
                        # Extract correct answers
                        if question_type == "check-all":
                            correct_answers = request.form.getlist(f'subform-{question_number}-correctCheckboxes')
                        elif question_type == "multiple-choice" or question_type == "true-false":
                            correct_answers = request.form.get(f'subform-{question_number}-correctRadio')
                        
                        # Extract all answers
                        all_answers = []
                        for option in ['answer1', 'answer2', 'answer3', 'answer4']:
                            answer = request.form.get(f'subform-{question_number}-{option}')
                            all_answers.append([answer, answer in correct_answers])
                        
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
                return redirect(url_for('auth.login'))
        else:
            print("Form validation failed. Form errors:", form.errors)  # Debug: Print form errors
    return render_template('create_quiz.html', form=form)


'''
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
    return redirect(url_for('create_quiz.create_q'))'''