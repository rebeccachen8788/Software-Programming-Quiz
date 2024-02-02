# Source: https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# accessed 2/2/24

from flask import Flask
from .db_connector import get_db_connection


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    db_connection = get_db_connection()
    db_connection.ping(True)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    return app