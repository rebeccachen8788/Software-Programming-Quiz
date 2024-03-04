from flask import Blueprint, render_template, request, redirect, url_for, flash

from .db_connector import get_db_connection
from .auth import login_required
bp = Blueprint('creator_homepage', __name__)


@bp.route('/creator-home')
@login_required # prevents unauthenticated users from accessing this page
def creator_homepage():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT quizID FROM Quiz")
    quizzes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('creator_homepage.html', quizzes=quizzes)


@bp.route('/quiz_details/<int:quizID>')
@login_required
def quiz_questions(quizID):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # retrieve quizID associated with the linkID
    cursor.execute("SELECT * FROM Question WHERE quizID = %s", (quizID,))
    questions = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('quiz_details.html', quizID=quizID, questions=questions)