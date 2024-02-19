# SOURCE: https://github.com/mailjet/mailjet-apiv3-python?tab=readme-ov-file#simple-post-request

from flask import Blueprint, render_template, request
from mailjet_rest import Client
from .db_connector import get_db_connection, execute_query
import uuid

bp = Blueprint('email', __name__)

# Configure Mailjet API keys
# This keys are form the account I created.
API_KEY = '4f4724f09fd7d7127aa5f0d5d17fed1d'
API_SECRET = 'e069a58167f81de0de76dfb6ec4c3255'
mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')


def generate_quiz_link():
    # Generate a unique identifier for the quiz link
    unique_id = str(uuid.uuid4())
    return f"http://testlink.com/quiz/{unique_id}"


def send_email(names, email_addresses, messages):
    if email_addresses and len(email_addresses) > 0:
        for receiver, message, name in zip(email_addresses, messages, names):
            quiz_link = generate_quiz_link()

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


# Render quiz access page with mock data
@bp.route('/quiz_send', methods=['GET', 'POST'])
def quiz_send():
    if request.method == 'POST':
        names = request.form.getlist('name[]')
        emails = request.form.getlist('email[]')
        messages = request.form.getlist('message[]')
        # quiz_id = request.form['quiz_id']
        send_email(names, emails, messages)
        return render_template('email_sent.html')
    
    # This if statement can be used to send multiple emails for a future time:
    # if request.method == 'POST':
    #     names = request.form.getlist('name[]')
    #     emails = request.form.getlist('email[]')
        
    #     # Loop through the lists of names and emails
    #     for name, email in zip(names, emails):
    #         send_email(name, email)
    #     return "Emails sent successfully!"  # Can redirect or render another template here
    
    else:
        return "Method Not Allowed", 405
        # return render_template('quiz_send.html')

# Route to send quiz results
@bp.route('/send_quiz_results', methods=['POST'])
def send_quiz_results():
    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        quiz_creator_email = get_quiz_creator_email(quiz_id)
        quiz_title = request.form.get('quiz_title')
        quiz_results = request.form.get('quiz_results')
        if quiz_creator_email:
            send_quiz_results_email(quiz_creator_email, quiz_title, quiz_results)
            return "Quiz results email sent to the creator!"
        else:
            return "Failed to send quiz results email. Quiz creator not found."
    else:
        return "Method Not Allowed", 405

@bp.route('/email_sent', methods=['GET', 'POST'])
def email_sent():
    return render_template('email_sent.html')
