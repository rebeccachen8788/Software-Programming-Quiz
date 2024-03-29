from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectMultipleField, TextAreaField, SubmitField, widgets
from wtforms.validators import Optional
from .email_func import send_quiz_results_email
import re

from .db_connector import get_db_connection

bp = Blueprint('take_quiz', __name__)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DynamicQuizForm(FlaskForm):
    submit = SubmitField('Submit')


@bp.route('/take_quiz/<int:linkID>', methods=['GET', 'POST'])
def show_quiz(linkID):
    global answer_details
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # retrieve quizID associated with the linkID
    cursor.execute("SELECT quizID, completed FROM Results WHERE linkID = %s", (linkID,))
    result = cursor.fetchall()

    if not result:
        flash('There was an issue retrieving your quiz. Please try again.', 'error')
        return render_template('error_page.html')
    else:
        completed = result[0]['completed']
        if completed:
            flash('There was an issue retrieving your quiz. Please try again.', 'error')
            return render_template('error_page.html')
        quizID = result[0]['quizID']

    # Fetch title of the quiz
    cursor.execute("SELECT title FROM Quiz WHERE quizID = %s", (quizID,))
    quiz = cursor.fetchone()
    quiz_title = quiz['title']

    # Fetch time limit for the quiz
    cursor.execute("SELECT time FROM Quiz WHERE quizID = %s", (quizID,))
    data = cursor.fetchone()
    time = data['time']

    # Fetch questions for the quiz
    cursor.execute("SELECT * FROM Question WHERE quizID = %s", (quizID,))
    questions = cursor.fetchall()

    class FilledQuizForm(DynamicQuizForm):
        pass

    for question in questions:
        field_name = f"question_{question['questionID']}"
        cursor.execute("SELECT * FROM Answers WHERE questionID = %s", (question['questionID'],))
        answers = cursor.fetchall()
        choices = [(str(answer['answerID']), answer['details']) for answer in answers]

        if question['type'] == 'true-false' or question['type'] == 'multiple-choice':
            field = RadioField(question['details'], choices=choices, validators=[Optional()])
        elif question['type'] == 'check-all':
            field = MultiCheckboxField(question['details'], choices=choices, validators=[Optional()])
        elif question['type'] == 'freeform':
            field = TextAreaField(question['details'], validators=[Optional()])

        setattr(FilledQuizForm, field_name, field)
    form = FilledQuizForm()

    # collect response data
    if request.method == 'POST':
        responses = []
        for field_name, value in form.data.items():
            if field_name.startswith('question_'):
                question_id = int(field_name.split('_')[1])
                if isinstance(value, list):  # For fields that allow multiple answers like checkboxes
                    if not value:
                        responses.append((quizID, question_id, value))
                    for answer in value:
                        responses.append((quizID, question_id, answer))
                else:  # For radio fields and text areas
                    responses.append((quizID, question_id, value))
        # get amount of time it took for quiz taker to complete the quiz from the front-tend
        time_remaining = request.form.get('time_remaining')
        if time_remaining.startswith('-'):
            time_used = time
        else:
            time_used = calculate_time_used(time, time_remaining=request.form.get('time_remaining'))

        # Save responses to the database
        try:
            total_score = 0
            for quizID, question_id, answer in responses:
                # answer represent answerID (except for the freeform) therefore I am fetching answer details
                cursor.execute("SELECT type, score FROM Question WHERE questionID = %s", (question_id,))
                question = cursor.fetchall()

                if question:
                    if question[0]['type'] == "freeform":
                        if answer:
                            total_score += int(question[0]['score'])
                            cursor.execute("INSERT INTO Response (linkID, questionID, response) VALUES (%s, %s, %s)",
                                           (linkID, question_id, answer))
                        else:
                            # If no answer provided
                            cursor.execute("INSERT INTO Response (linkID, questionID, response) VALUES (%s, %s, %s)",
                                           (linkID, question_id, "No response"))
                    else:
                        # If no answer provided
                        if not answer:
                            cursor.execute("INSERT INTO Response (linkID, questionID, response) VALUES (%s, %s, %s)",
                                           (linkID, question_id, "No response"))
                        else:
                            cursor.execute("SELECT details, correct FROM Answers WHERE answerID = %s", (answer,))
                            results = cursor.fetchall()
                            if not results:
                                continue
                            answer_details = results[0]['details']
                            is_correct = results[0]['correct']
                            question_score = question[0]['score']

                            # if check-all, adjust how much each correct answer weigh
                            if question[0]['type'] == "check-all":
                                # find out how many correct answers
                                cursor.execute("SELECT * FROM Answers WHERE questionID = %s AND correct = %s",
                                               (question_id, True,))
                                all_answers = cursor.fetchall()
                                # print("len of all answers for question:", question_id, len(all_answers))
                                question_score = question_score / len(all_answers)

                            # update the score
                            if is_correct:
                                total_score += question_score
                            # submit to responses
                            cursor.execute("INSERT INTO Response (linkID, questionID, response) VALUES (%s, %s, %s)",
                                           (linkID, question_id, answer_details))

            # round to nearest double digits
            total_score = round(total_score, 2)
            # print(total_score)
            # add total score and update completed
            cursor.execute("UPDATE Results SET totalScore = %s, completed = %s, timeTaken = %s WHERE linkID = %s",
                           (total_score, True, time_used, linkID))
            db.commit()
        except Exception as err:
            print(f"Error1: {err}")
            db.rollback()
            flash('There was an issue submitting your responses. Please try again.', 'error')
        db.commit()

        # Trigger sending quiz results email after quiz submission is processed
        try:
            # Fetch the taker's email from the Quiz_Taker table
            cursor.execute("""
                SELECT takerEmail
                FROM Quiz_Taker
                WHERE takerID = (
                    SELECT takerID FROM Results WHERE linkID = %s
                )
            """, (linkID,))
            quiz_taker_email = cursor.fetchone()['takerEmail']

            # Fetch quiz creator's email using the quizID associated with the linkID in the Results table
            cursor.execute("""
                SELECT creatorID, title
                FROM Quiz
                WHERE quizID = (
                    SELECT quizID FROM Results WHERE linkID = %s
                )
            """, (linkID,))
            quiz_info = cursor.fetchone()
            creator_id = quiz_info['creatorID']
            quiz_title = quiz_info['title']

            # Fetch creator's email using the creatorID from the Quiz_Creator table
            cursor.execute("SELECT creatorEmail FROM Quiz_Creator WHERE creatorID = %s", (creator_id,))
            creator_email = cursor.fetchone()['creatorEmail']

            send_quiz_results_email(creator_email, quiz_taker_email, linkID, quiz_title)

        except Exception as e:
            print(f"Error sending quiz results email: {e}")

        cursor.close()
        db.close()
        # this should be directed to the confirmation page
        return render_template('confirmation.html')
    else:
        db.commit()
        cursor.close()
        db.close()
        # Handling GET request or invalid form submission
        return render_template('take_quiz.html', form=form, quizID=quizID, time_limit = time, quiz_title=quiz_title)

def calculate_time_used(time, time_remaining):
    # split time_remaining by both letter and comma, leaving just ints
    time_remaining = re.split(r"\D", time_remaining)
    hours = int(time_remaining[0])
    minutes = int(time_remaining[2])
    return time - (hours * 60 + minutes)
