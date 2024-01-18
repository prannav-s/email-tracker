import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os.path

def send_email():
    sender_email = 'prannav.shankar@gmail.com'
    recipient_email = 'prannav.shankar@gmail.com'
    subject = 'Daily Questionnaire'
    body = '''Hi Prannav! I hope you had a good day! Here is your daily questionnaire, please fill out all the questions below:

Mood:
Portfolio value:
Calories:
Gym (True or False):
Weight:'''

    # Load credentials
    creds = None
    token_path = 'token.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.send'])
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Create the Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Create the email message
    message = MIMEMultipart()
    message['to'] = recipient_email
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)

    # Send the email
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        service.users().messages().send(userId=sender_email, body={'raw': raw_message}).execute()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Rest of the code...


