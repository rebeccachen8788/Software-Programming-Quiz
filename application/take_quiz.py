from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectMultipleField, TextAreaField, SubmitField, widgets, ValidationError
from wtforms.validators import DataRequired, Optional

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
        return render_template('c.html')
    else:
        completed = result[0]['completed']
        if completed:
            flash('There was an issue retrieving your quiz. Please try again.', 'error')
            return render_template('error_page.html')
        quizID = result[0]['quizID']

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
    if request.method == 'POST' and form.validate():
        responses = []
        for field_name, value in form.data.items():
            if field_name.startswith('question_'):
                question_id = int(field_name.split('_')[1])
                if isinstance(value, list):  # For fields that allow multiple answers like checkboxes
                    for answer in value:
                        responses.append((quizID, question_id, answer))
                else:  # For radio fields and text areas
                    responses.append((quizID, question_id, value))
        # Save responses to the database
        try:
            total_score = 0
            for quizID, question_id, answer in responses:
                # answer represent answerID (except for the freeform) therefore I am fetching answer details
                cursor.execute("SELECT type, score FROM Question WHERE questionID = %s", (question_id,))
                question = cursor.fetchall()

                if question:
                    if question[0]['type'] == "freeform":
                        cursor.execute("INSERT INTO Response (linkID, questionID, response) VALUES (%s, %s, %s)",
                                       (linkID, question_id, answer))
                        if answer:
                            total_score += int(question[0]['score'])
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
                            cursor.execute("SELECT * FROM Answers WHERE questionID = %s AND correct = %s", (question_id, True,))
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
            print(total_score)
            # add total score and update completed
            cursor.execute("UPDATE Results SET totalScore = %s, completed = %s WHERE linkID = %s", (total_score, True, linkID))
            db.commit()
        except Exception as err:
            print(f"Error1: {err}")
            db.rollback()
            flash('There was an issue submitting your responses. Please try again.', 'error')
        db.commit()
        cursor.close()
        db.close()
        # this should be directed to the confirmation page
        return render_template('confirmation.html')
    else:
        db.commit()
        cursor.close()
        db.close()
        # Handling GET request or invalid form submission
        return render_template('take_quiz.html', form=form, quizID=quizID)


