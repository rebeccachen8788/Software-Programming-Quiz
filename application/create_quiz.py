from flask import Flask, Blueprint, render_template, redirect, url_for, request
from .db_connector import get_db_connection
from .auth import login_required

bp = Blueprint('create_quiz', __name__, url_prefix='/')


@bp.route('/create_quiz', methods=['GET', 'POST'])
# @login_required -> prevents unauthenticated users from accessing this page
def create_q():
    if request.method == 'POST':
        # Process the selected question type and prepare the next part of the form
        question_type = request.form.get('questionType')
        return render_template('create_quiz.html', question_type=question_type)
    else:
        # First visit to the form, no question type selected
        return render_template('create_quiz.html', question_type=None)


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