from flask import Flask, redirect, render_template, request, session, url_for
from .db_connector import get_db_connection, execute_query
from flask import Blueprint, render_template, request
from itertools import groupby
from operator import itemgetter

bp = Blueprint('start_quiz', __name__, url_prefix='/')

@bp.route("/start_quiz/<int:linkID>", methods=["GET"])
@bp.route("/start_quiz", defaults={'linkID': None}, methods=["GET"])
def start_quiz(linkID):
    time = None
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # retrieve time limit for the quiz
    cursor.execute("SELECT time FROM Quiz JOIN Results ON Quiz.quizID = Results.quizID WHERE Results.linkID = %s", (linkID,))
    data = cursor.fetchone()
    if data: 
        time = data['time']
    cursor.close()
    # Pass linkID to the template, which might be None if not provided
    return render_template("start_quiz.html", linkID=linkID, time=time)