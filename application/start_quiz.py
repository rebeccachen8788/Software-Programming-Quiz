from flask import Flask, redirect, render_template, request, session, url_for
from .db_connector import get_db_connection, execute_query
from flask import Blueprint, render_template, request
from itertools import groupby
from operator import itemgetter

bp = Blueprint('start_quiz', __name__, url_prefix='/')

@bp.route("/start_quiz/<int:linkID>", methods=["GET"])
@bp.route("/start_quiz", defaults={'linkID': None}, methods=["GET"])
def start_quiz(linkID):
    # Pass linkID to the template, which might be None if not provided
    return render_template("start_quiz.html", linkID=linkID)