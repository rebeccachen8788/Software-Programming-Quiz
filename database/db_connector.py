import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv, find_dotenv

# Load our environment variables from the .env file in the root of our project.
load_dotenv(find_dotenv())

# Set the variables in our application with those environment variables
host = os.environ.get("HOST")
user = os.environ.get("DBUSER")
passwd = os.environ.get("PASSWORD")
db = os.environ.get("DB")


def get_db_connection():
    try:
        connection = mysql.connector.connect(host=host, database=db, user=user, password=passwd)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_info)
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


def execute_query(db_connection=None, query=None, query_params=()):
    """
    Executes a given SQL query on the given db connection and optionally returns a Cursor object.

    :param db_connection: a mysql.connector connection object.
    :param query: string containing SQL query.
    :param query_params: parameters to pass along with the query for safe execution.

    :return: A Cursor object on success, None on failure.
    """
    if db_connection is None:
        print("No connection to the database found!")
        return None

    if query is None or len(query.strip()) == 0:
        print("Query is empty! Please pass a SQL query in query.")
        return None

    try:
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary=True to get DictCursor functionality
        print(f"Executing {query} with {query_params}")
        cursor.execute(query, query_params)
        db_connection.commit()  # Commit to save changes to the database
        return cursor
    except Error as e:
        print(f"Error occurred: {e}")
        db_connection.rollback()  # Rollback in case of any error
        return None
