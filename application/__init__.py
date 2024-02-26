# Source: https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# accessed 2/2/24

from flask import Flask, render_template, redirect, url_for, request
from .db_connector import get_db_connection, execute_query
from .results import show_results, get_responses_for_taker_quiz_by_link_id

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
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

    from .auth import login_required

    from . import take_quiz
    app.register_blueprint(take_quiz.bp)

    from . import creator_homepage
    app.register_blueprint(creator_homepage.bp)

    
    @app.route("/")
    def root():
        return render_template("homepage.html")
    
    from . import results
    app.register_blueprint(results.bp)

    return app