import flask_login
from flask import Flask, redirect, render_template, request, session, url_for
from .db_connector import get_db_connection, execute_query
from itertools import groupby
from operator import itemgetter

def get_quiz_results_for_creator(creator_id):
    """
    Fetches all quiz results for quizzes created by the specified creatorID.
    """
    query = """
    SELECT R.linkID, R.quizID, R.takerID, QT.takerEmail, R.timeTaken, R.totalScore, R.completed, Q.time as quizTime
    FROM Results R
    JOIN Quiz Q ON R.quizID = Q.quizID
    JOIN Quiz_Taker QT ON R.takerID = QT.takerID
    WHERE Q.creatorID = %s;
    """
    db = get_db_connection()
    if db is None:
        print("No connection to the database.")
        return []

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, (creator_id,))
        results = cursor.fetchall()
        for result in results:
            result['totalScore'] = int(result['totalScore'])
        
        # Sorting the results by totalScore
        sorted_results = sorted(results, key=lambda x: x['totalScore'], reverse=True)
    except Error as e:
        print(f"Error fetching quiz results for creator {creator_id}: {e}")
        return []
    finally:
        cursor.close()
        db.close()
    return sorted_results

def show_results():
    """
    Renders a template with the results for quizzes belonging to the logged-in creator.
    """
    if 'user_id' not in session:
        # Assuming there's a login view to redirect to if not logged in
        return redirect(url_for('auth.login'))

    # Fetch sorted results as before
    creator_id = session['user_id']
    sorted_results = get_quiz_results_for_creator(creator_id)

    # Ensure results are sorted by quizID before grouping
    sorted_results.sort(key=itemgetter('quizID'))
    
     # Group results by quizID
    grouped_results = {}
    dropdown_data = {}  # New structure for dropdown data
    for key, group in groupby(sorted_results, key=itemgetter('quizID')):
        results_list = list(group)
        grouped_results[key] = results_list
        # Populate dropdown data with takerIDs and their email for each quiz
        dropdown_data[key] = [(result['takerID'], result['takerEmail'], result['linkID'], result['totalScore']) for result in results_list]
    return render_template('results.html', grouped_results=grouped_results, dropdown_data=dropdown_data)

def get_responses_for_taker_quiz_by_link_id(link_id):
    query = """
    SELECT 
        Q.details AS question_details, 
        R.response, 
        A.correct
    FROM 
        Question Q
    JOIN 
        Response R ON Q.questionID = R.questionID
    LEFT JOIN 
        Answers A ON R.questionID = A.questionID AND R.response = A.details
    WHERE 
        R.linkID = %s;
    """
    db = get_db_connection()
    responses = []
    if db is not None:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, (link_id,))
            responses = cursor.fetchall()
        except Error as e:
            print(f"Error fetching responses for link ID {link_id}: {e}")
        finally:
            cursor.close()
            db.close()
    return responses