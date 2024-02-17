# SOURCE: https://mailtrap.io/blog/python-send-email/#How-to-send-emails-to-multiple-recipients-using-Python

from flask import Blueprint, render_template, request
from mailjet_rest import Client
import uuid

email_bp = Blueprint('email', __name__)

# Configure Mailjet API keys
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


# Render quiz access page with mock data
@email_bp.route('/quiz_send', methods=['GET', 'POST'])
def quiz_send():
    if request.method == 'POST':
        names = request.form.getlist('name[]')
        emails = request.form.getlist('email[]')
        messages = request.form.getlist('message[]')
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
        return render_template('quiz_send.html')

@email_bp.route('/email_sent', methods=['GET', 'POST'])
def email_sent():
    return render_template('email_sent.html')
