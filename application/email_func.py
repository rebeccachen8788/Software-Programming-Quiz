# SOURCE: https://github.com/mailjet/mailjet-apiv3-python?tab=readme-ov-file#simple-post-request

from flask import Blueprint, render_template, request, session, url_for
from mailjet_rest import Client
from .db_connector import get_db_connection, execute_query

bp = Blueprint('email', __name__)

# Configure Mailjet API keys
# This keys are form the account I created.
API_KEY = '4f4724f09fd7d7127aa5f0d5d17fed1d'
API_SECRET = 'e069a58167f81de0de76dfb6ec4c3255'
mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

def get_or_create_taker_id(email, name):
    """Retrieve or create a Quiz_Taker and return the takerID."""
    db_connection = get_db_connection()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            # Check if Quiz_Taker with the given email already exists
            cursor.execute("SELECT takerID FROM Quiz_Taker WHERE takerEmail = %s", (email,))
            taker_id = cursor.fetchone()
            if taker_id:
                return taker_id[0]  # Return existing takerID
            else:
                # Insert a new Quiz_Taker
                cursor.execute("INSERT INTO Quiz_Taker (takerEmail, firstName) VALUES (%s, %s)", (email, name))
                db_connection.commit()
                return cursor.lastrowid  # Return auto-generated takerID
        except Exception as e:
            print(f"Error retrieving or creating Quiz_Taker: {e}")
            db_connection.rollback()
        finally:
            cursor.close()
            db_connection.close()
    return None


def insert_new_link_id(quiz_id, email):
    """Insert a new linkID into the Results table for the provided quizID and takerID."""
    db_connection = get_db_connection()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            
            # Check if takerID exists in Quiz_Taker table
            cursor.execute("SELECT takerID FROM Quiz_Taker WHERE takerEmail = %s", (email,))
            result = cursor.fetchone()
            if not result:
                print("Error: takerID does not exist in Quiz_Taker table.")
                return None
            
            # Insert new linkID into Results table
            cursor.execute("INSERT INTO Results (quizID, takerID) VALUES (%s, %s)", (quiz_id, result[0]))
            db_connection.commit()
            
            return cursor.lastrowid  # Return auto-generated linkID
        except Exception as e:
            print(f"Error inserting new linkID into Results table: {e}")
            db_connection.rollback()
        finally:
            cursor.close()
            db_connection.close()
    return None


def generate_quiz_link(link_id):
    # Generate quiz taking link based on database
    #NOTE:Will need to change based on what flip server we are hosting on
    return f"http://127.0.0.1:12118/start_quiz/{link_id}"


# def get_quiz_id_from_link(unique_id):
#     """Retrieve the quizID associated with the provided linkID."""
#     query = """
#         SELECT quizID
#         FROM Results
#         WHERE linkID = %s
#     """
#     db_connection = get_db_connection()  # Assuming you have a function to get the database connection
#     if db_connection:
#         cursor = execute_query(db_connection, query, (unique_id,))
#         if cursor:
#             result = cursor.fetchone()
#             db_connection.close()
#             if result:
#                 return result['quizID']
#     return None


def send_email(name, email_address, message, link_id):
    quiz_link = generate_quiz_link(link_id)

    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'virgenlg@oregonstate.edu',
                    'Name': 'SWE Programming Quiz'
                },
                'To': [
                    {
                        'Email': email_address,
                        'Name': name
                    }
                ],
                'Subject': 'Quiz Invitation',
                'TextPart': f"Hello {name},\n\n{message}\n\nLink to the quiz: {quiz_link}."
            }
        ]
    }

    # Send the email
    response = mailjet.send.create(data=data)
    print(f'Sent to {email_address}')


def get_quiz_creator_email(quiz_id):
    """Retrieve the email address of the quiz creator from the database."""
    query = """
        SELECT creatorEmail 
        FROM Quiz_Creator 
        WHERE creatorID = (
            SELECT creatorID 
            FROM Quiz 
            WHERE quizID = %s
        )
    """
    db_connection = get_db_connection()
    if db_connection:
        cursor = execute_query(db_connection, query, (quiz_id,))
        if cursor:
            result = cursor.fetchone()
            db_connection.close()
            if result:
                return result['creatorEmail']
    return None

# I think i might not need this function
# def get_creator_id_from_quiz_id(quiz_id):
#     """Retrieve the creator ID associated with the provided quiz ID."""
#     # Convert quiz_id to integer
#     quiz_id = int(quiz_id)
    
#     query = """
#         SELECT creatorID
#         FROM Quiz
#         WHERE quizID = %s
#     """
#     db_connection = get_db_connection()
#     if db_connection:
#         cursor = execute_query(db_connection, query, (quiz_id,))
#         if cursor:
#             result = cursor.fetchone()
#             db_connection.close()
#             if result:
#                 return result['creatorID']
#     return None


def fetch_user_quizzes(user_id):
    # Assume you have a function to get a database connection
    db_connection = get_db_connection()

    if db_connection:
        try:
            # Execute a query to fetch quizzes for the given user ID
            query = "SELECT quizID FROM Quiz WHERE creatorID = %s"
            cursor = db_connection.cursor()
            cursor.execute(query, (user_id,))
            
            # Fetch all rows as a list of dictionaries
            quizzes = [{'QuizID': row[0]} for row in cursor.fetchall()]
            
            # Close cursor and database connection
            cursor.close()
            db_connection.close()
            
            return quizzes
        except Exception as e:
            print(f"Error fetching user quizzes: {e}")
            return []  # Return an empty list if there's an error
    else:
        print("Error: Unable to connect to the database.")
        return []  # Return an empty list if there's no database connection


@bp.route('/quiz_send', methods=['GET', 'POST'])
def quiz_send():
    if request.method == 'POST':
        name = request.form.get('name')  # Assuming single name field
        email = request.form.get('email')  # Assuming single email field
        message = request.form.get('message')  # Assuming single message field
        quiz_id = request.form['quiz_id']  # Assuming we get the quiz ID from the form

        # Fetch the creator ID from the database using the quiz ID
        creator_id = session.get('user_id')
        if not creator_id:
            return "Quiz not found or expired.", 404
        
        # Insert a new Quiz_Taker if not already exists
        taker_id = get_or_create_taker_id(email, name)
        if not taker_id:
            return "Failed to create or retrieve Quiz_Taker.", 500
        
        # Insert a new linkID for the recipient
        link_id = insert_new_link_id(quiz_id, email)
        if link_id:
            # Send email to the recipient
            send_email(name, email, message, link_id)
            return render_template('email_sent.html')
        else:
            # Handle error if linkID insertion fails
            return "Failed to generate quiz link. Please try again.", 500
    else:
        # Fetch quizzes created by the current user
        user_id = session.get('user_id')  # Assuming user ID is stored in session
        if user_id:
            user_quizzes = fetch_user_quizzes(user_id)  # Implement this function according to your database structure
        else:
            user_quizzes = []
        
        return render_template('quiz_send.html', quizzes=user_quizzes)


# Route to send quiz results
# The following was grabbed and modified by the code from result.py on function show_taker_responses
@bp.route('/send_quiz_results', methods=['POST'])
def send_quiz_results():
    if request.method == 'POST':
        link_id = request.form.get('link_id')
        quiz_id = request.form.get('quiz_id')
        quiz_title = request.form.get('quiz_title')

        # Ensure link_id and quiz_id are provided
        if not link_id or not quiz_id:
            return "Link ID and Quiz ID are required.", 400
        
        # Retrieve the quiz creator's email
        quiz_creator_email = get_quiz_creator_email(quiz_id)
        if not quiz_creator_email:
            return "Failed to send quiz results email. Quiz creator not found.", 404

        # Send quiz results email
        try:
            # Send email with the link to view quiz results
            send_quiz_results_email(quiz_creator_email, quiz_title, link_id)
            return "Quiz results email sent to the creator!"
        except Exception as e:
            return f"Failed to send quiz results email: {str(e)}", 500
    else:
        return "Method Not Allowed", 405


# def get_responses_for_taker_quiz_by_link_id(link_id):
#     db_connection = get_db_connection()
#     cursor = db_connection.cursor(dictionary=True)
#     try:
#         # Assuming you have a SQL query to fetch responses based on the link_id
#         cursor.execute("""
#             SELECT R.*, Q.details AS question_details
#             FROM Response R
#             JOIN Question Q ON R.questionID = Q.questionID
#             WHERE R.linkID = %s;
#         """, (link_id,))
#         responses = cursor.fetchall()
#     except Exception as e:
#         print(f"An error occurred while fetching responses: {e}")
#         responses = []
#     finally:
#         cursor.close()
#         db_connection.close()
#     return responses


# def get_taker_email_and_responses(link_id):
#     db_connection = get_db_connection()
#     cursor = db_connection.cursor(dictionary=True)
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
        
#         # Fetch responses for the link_id
#         # Assuming this part is done in a separate function or logic
#         responses = get_responses_for_taker_quiz_by_link_id(link_id)

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         taker_email = 'Error fetching email'
#         responses = []

#     finally:
#         cursor.close()
#         db_connection.close()
    
#     return taker_email, responses


def send_quiz_results_email(quiz_creator_email, quiz_taker, link_id):
    # Generate URL for viewing quiz results
    results_url = url_for('results.show_taker_responses', link_id=link_id, _external=True)

    # Define the email message
    email_data = {
        'Messages': [
            {
                'From': {
                    'Email': 'virgenlg@oregonstate.edu',
                    'Name': 'Software Programming Quiz'
                },
                'To': [
                    {
                        'Email': quiz_creator_email,
                        'Name': 'Quiz Creator'
                    }
                ],
                'Subject': f'Results for "{quiz_taker}" Quiz',
                'TextPart': f'Hello,\n\nHere are the results for the "{quiz_taker}" Quiz.\n\n'
                            f'You can view the results by clicking on the following link:\n{results_url}'
            }
        ]
    }

    # Send the email
    response = mailjet.send.create(data=email_data)

    # Check if the request was successful
    if response.status_code == 200:
        print('Quiz results email sent successfully to the creator!')
    else:
        print(f'Failed to send quiz results email to the creator. Status code: {response.status_code}')
        print(response.json())


# def store_link_quiz_association(link_id, quiz_id):
#     query = """
#         INSERT INTO Results (linkID, quizID, takerID, timeTaken)
#         VALUES (%s, %s, DEFAULT, NULL)
#     """
#     db_connection = get_db_connection()
#     if db_connection:
#         try:
#             cursor = db_connection.cursor()
#             cursor.execute(query, (link_id, quiz_id))
#             db_connection.commit()
#         except Exception as e:
#             print(f"Error storing link-quiz association: {e}")
#             db_connection.rollback()
#         finally:
#             cursor.close()
#             db_connection.close()
#     else:
#         print("Error: Unable to connect to the database.")


@bp.route('/email_sent', methods=['GET', 'POST'])
def email_sent():
    return render_template('email_sent.html')
