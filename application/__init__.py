# Source: https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# accessed 2/2/24

from flask import Flask, render_template, redirect, session, url_for, request
from .db_connector import get_db_connection

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
    
    from . import email_func
    app.register_blueprint(email_func.bp)

    from . import take_quiz
    app.register_blueprint(take_quiz.bp)

    from . import creator_homepage
    app.register_blueprint(creator_homepage.bp)

    from . import results
    app.register_blueprint(results.bp)
    
    from . import settings
    app.register_blueprint(settings.bp)
    
    @app.route("/")
    def root():
        if 'user_id' in session:
            return redirect(url_for('creator_homepage.creator_homepage'))
        return render_template("homepage.html")

    from . import start_quiz
    app.register_blueprint(start_quiz.bp)

    return app