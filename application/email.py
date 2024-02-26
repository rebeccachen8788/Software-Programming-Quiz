# SOURCE: https://github.com/mailjet/mailjet-apiv3-python?tab=readme-ov-file#simple-post-request

from flask import Blueprint, render_template, request
from mailjet_rest import Client
from .db_connector import get_db_connection, execute_query

bp = Blueprint('email', __name__)

# Configure Mailjet API keys
# This keys are form the account I created.
API_KEY = '4f4724f09fd7d7127aa5f0d5d17fed1d'
API_SECRET = 'e069a58167f81de0de76dfb6ec4c3255'
mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

def insert_new_link_id(quiz_id, taker_email):
    """Inserts a new linkID into the Results table for the provided quizID."""
    query = "INSERT INTO Results (quizID, takerID) VALUES (%s, (SELECT takerID FROM Quiz_Taker WHERE takerEmail = %s))"
    db_connection = get_db_connection()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute(query, (quiz_id, taker_email))
            db_connection.commit()
            return cursor.lastrowid  # Return the auto-generated linkID
        except Exception as e:
            print(f"Error inserting new linkID into Results table: {e}")
            db_connection.rollback()
        finally:
            cursor.close()
            db_connection.close()
    return None



def generate_quiz_link(link_id):
    # Generate quiz taking link based on database
    return f"/take_quiz/{link_id}"


def get_quiz_id_from_link(unique_id):
    """Retrieve the quizID associated with the provided linkID."""
    query = """
        SELECT quizID
        FROM Results
        WHERE linkID = %s
    """
    db_connection = get_db_connection()  # Assuming you have a function to get the database connection
    if db_connection:
        cursor = execute_query(db_connection, query, (unique_id,))
        if cursor:
            result = cursor.fetchone()
            db_connection.close()
            if result:
                return result['quizID']
    return None


def send_email(names, email_addresses, messages, link_ids):
    if email_addresses and len(email_addresses) > 0:
        for receiver, message, name, link_id in zip(email_addresses, messages, names, link_ids):
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
                                'Email': receiver,
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
            print(f'Sent to {receiver}')
    else:
        print("No email addresses provided.")

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


@bp.route('/quiz_send', methods=['POST'])
def quiz_send():
    if request.method == 'POST':
        names = request.form.getlist('name[]')
        emails = request.form.getlist('email[]')
        messages = request.form.getlist('message[]')
        quiz_id = request.form['quiz_id']  # Assuming you get the quiz ID from the form
        link_ids = []
        # Insert a new linkID for each recipient and store it in the link_ids list
        for email in emails:
            link_id = insert_new_link_id(quiz_id, email)
            if link_id:
                link_ids.append(link_id)
            else:
                # Handle error if linkID insertion fails
                return "Failed to generate quiz link. Please try again.", 500
        send_email(names, emails, messages, link_ids)
        return render_template('email_sent.html')    
    else:
        return render_template('quiz_send.html')

    
# Route to send quiz results
# The following was inpsired by the code from result.py on function show_taker_responses
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

        # Retrieve the quiz taker's email and responses
        taker_email, responses = get_taker_email_and_responses(link_id)

        # Render the HTML page with the data
        rendered_html = render_template('taker_responses.html', link_id=link_id, taker_email=taker_email, responses=responses)

        # Send quiz results email
        try:
            # Include the rendered HTML in the email body
            send_email(names=[quiz_creator_email], email_addresses=[quiz_creator_email], messages=[""], link_ids=[link_id])
            return "Quiz results email sent to the creator!"
        except Exception as e:
            return f"Failed to send quiz results email: {str(e)}", 500
    else:
        return "Method Not Allowed", 405    


def get_responses_for_taker_quiz_by_link_id(link_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    try:
        # Assuming you have a SQL query to fetch responses based on the link_id
        cursor.execute("""
            SELECT R.*, Q.details AS question_details
            FROM Response R
            JOIN Question Q ON R.questionID = Q.questionID
            WHERE R.linkID = %s;
        """, (link_id,))
        responses = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred while fetching responses: {e}")
        responses = []
    finally:
        cursor.close()
        db_connection.close()
    return responses


def get_taker_email_and_responses(link_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    try:
        # Fetching taker's email using link_id
        cursor.execute("""
            SELECT QT.takerEmail
            FROM Results R
            JOIN Quiz_Taker QT ON R.takerID = QT.takerID
            WHERE R.linkID = %s;
        """, (link_id,))
        result = cursor.fetchone()
        if result:
            taker_email = result['takerEmail']
        else:
            taker_email = 'Unknown'
        
        # Fetch responses for the link_id
        # Assuming this part is done in a separate function or logic
        responses = get_responses_for_taker_quiz_by_link_id(link_id)

    except Exception as e:
        print(f"An error occurred: {e}")
        taker_email = 'Error fetching email'
        responses = []

    finally:
        cursor.close()
        db_connection.close()
    
    return taker_email, responses


def send_quiz_results_email(quiz_creator_email, quiz_title, quiz_results):
    # Define the email message
    email_data = {
        'Messages': [
            {
                'From': {
                    'Email': 'your_email@example.com',
                    'Name': 'Your Name'
                },
                'To': [
                    {
                        'Email': quiz_creator_email,
                        'Name': 'Quiz Creator'
                    }
                ],
                'Subject': f'Results for "{quiz_title}" Quiz',
                'TextPart': f'Hello,\n\nHere are the results for the "{quiz_title}" Quiz:\n\n{quiz_results}'
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


def store_link_quiz_association(link_id, quiz_id):
    query = """
        INSERT INTO Results (linkID, quizID, takerID, timeTaken)
        VALUES (%s, %s, NULL, NULL)
    """
    db_connection = get_db_connection()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute(query, (link_id, quiz_id))
            db_connection.commit()
        except Exception as e:
            print(f"Error storing link-quiz association: {e}")
            db_connection.rollback()
        finally:
            cursor.close()
            db_connection.close()
    else:
        print("Error: Unable to connect to the database.")


@bp.route('/take_quiz/<unique_id>', methods=['GET'])
def take_quiz(unique_id):
    # Retrieve the associated quizID from the database based on the unique_id
    quiz_id = get_quiz_id_from_link(unique_id)
    if quiz_id:
        # Construct SQL query to retrieve quiz data based on the quiz_id
        query = """
            SELECT Quiz.*, Question.*, Answers.*
            FROM Quiz
            INNER JOIN Question ON Quiz.quizID = Question.quizID
            INNER JOIN Answers ON Question.questionID = Answers.questionID
            WHERE Quiz.quizID = %s
        """
        
        # Attempt to get database connection
        db_connection = get_db_connection()
        if db_connection:
            # Execute the SQL query
            cursor = execute_query(db_connection, query, (quiz_id,))
            if cursor:
                quiz_data = cursor.fetchall()  # Fetch all quiz data from the cursor
                if quiz_data:
                    # Pass quiz_data to the template for rendering
                    return render_template('take_quiz.html', quiz_data=quiz_data, link_id=unique_id)
                else:
                    return "Quiz not found or expired."  # Handle invalid quiz link
            else:
                return "Error: Unable to fetch quiz data from the database."  # Handle database query error
        else:
            return "Error: Unable to connect to the database."  # Handle database connection error
    else:
        return "Quiz link not found or expired."  # Handle invalid quiz link



@bp.route('/email_sent', methods=['GET', 'POST'])
def email_sent():
    return render_template('email_sent.html')
