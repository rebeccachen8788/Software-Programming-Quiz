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


@bp.route('/take_quiz/<int:quizID>', methods=['GET', 'POST'])
# eventually quizID needs to be replaced with the linkID
def show_quiz(quizID):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

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
            field = RadioField(question['details'], choices=choices, validators=[DataRequired()])
        elif question['type'] == 'check-all':
            field = MultiCheckboxField(question['details'], choices=choices, validators=[Optional()])
        elif question['type'] == 'freeform':
            field = TextAreaField(question['details'], validators=[DataRequired()])

        setattr(FilledQuizForm, field_name, field)

    form = FilledQuizForm()

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
            for quizID, question_id, answer in responses:
                cursor.execute("INSERT INTO Response (quizID, questionID, response) VALUES (%s, %s, %s)",
                               (quizID, question_id, answer))
            db.commit()
            flash('Your responses have been submitted successfully!', 'success')
        except Exception as err:
            print(f"Error: {err}")
            db.rollback()
            flash('There was an issue submitting your responses. Please try again.', 'error')
        db.commit()
        cursor.close()
        db.close()
        # this should be directed to the confirmation page
        return redirect(url_for('take_quiz.show_quiz', quizID=quizID))
    else:
        db.commit()
        cursor.close()
        db.close()
    # Handling GET request or invalid form submission
        return render_template('take_quiz.html', form=form, quizID=quizID)

