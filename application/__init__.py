# Source: https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# accessed 2/2/24

from flask import Flask, render_template, redirect, url_for, request
from .db_connector import get_db_connection, execute_query
from .results import show_results, get_responses_for_taker_quiz_by_link_id

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='randomKey'
    )

    db_connection = get_db_connection()
    db_connection.ping(True)
     
    from . import auth
    app.register_blueprint(auth.bp)

    from . import create_quiz
    app.register_blueprint(create_quiz.bp)
    
    from . import email
    app.register_blueprint(email.bp)

    # from .auth import login_required

    from . import take_quiz
    app.register_blueprint(take_quiz.bp)
    
    @app.route("/")
    # @login_required -> prevents unauthenticated users from accessing this page
    def root():
        return render_template("homepage.html")
    
    from . import results
    app.register_blueprint(results.bp)
    # app.route('/results')
    # def results():
    #     return show_results()
    
    # @app.route('/responses/<int:link_id>')
    # def show_taker_responses(link_id):
    #     # Use link_id to fetch the responses for the specific quiz attempt
    #     responses = get_responses_for_taker_quiz_by_link_id(link_id)
    #     db = get_db_connection()
    #     cursor = db.cursor(dictionary=True)
    #     # Assume you have a function or logic here to fetch responses based on link_id
    #     try:
    #         # Fetching taker's email using link_id
    #         cursor.execute("""
    #             SELECT QT.takerEmail
    #             FROM Results R
    #             JOIN Quiz_Taker QT ON R.takerID = QT.takerID
    #             WHERE R.linkID = %s;
    #         """, (link_id,))
    #         result = cursor.fetchone()
    #         if result:
    #             taker_email = result['takerEmail']
    #         else:
    #             taker_email = 'Unknown'
            
    #         # Fetch responses for the link_id (Assuming this part is done in get_responses_for_taker_quiz_by_link_id function)
    #         responses = get_responses_for_taker_quiz_by_link_id(link_id)

    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         taker_email = 'Error fetching email'
    #         responses = []

    #     finally:
    #         cursor.close()
    #         db.close()
    #     return render_template('taker_responses.html', responses=responses, link_id=link_id, taker_email=taker_email)

    return app