import base64
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import sqlite3
from google.oauth2.credentials import Credentials
from datetime import datetime

# Connect to SQLite database (or create a new one)
conn = sqlite3.connect('responses.db')
cursor = conn.cursor()

# Create a table to store responses
cursor.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day DATE,
        mood INTEGER,
        portfolio DOUBLE,
        calories INTEGER,
        gym BOOLEAN,
        weight DOUBLE
    )
''')
conn.commit()

# Function to store responses in the database
def store_responses(date, mood, portfolio, calories, gym, weight):
    cursor.execute('''
        INSERT INTO responses (day, mood, portfolio, calories, gym, weight)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, mood, portfolio, calories, gym, weight))
    conn.commit()

# Function to extract and store responses from the email
def process_email(service, message_id):
    try:
        # Get the email message
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = message['payload']
        parts = payload.get('parts', [])

        # Find the part containing text/plain
        plain_text_part = next((part for part in parts if part['mimeType'] == 'text/plain'), None)

        # Check if the plain text part is found
        if plain_text_part:
            # Extract and decode body data
            body_data = plain_text_part['body']['data']
            body = base64.urlsafe_b64decode(body_data.encode('UTF-8')).decode('UTF-8')

            # Now, you can use the 'body' variable as the plain text email content
            print("Plain Text Body:", body)
        else:
            print("No plain text part found in the email.")

        # Extract and decode body
        response_lines = body.split("\n")

        # Extract responses
        date = datetime.now().date().strftime("%Y-%m-%d")
        mood = int(response_lines[5].split(":")[1].strip())
        portfolio = response_lines[6].split(":")[1].strip()
        calories = response_lines[7].split(":")[1].strip()
        gym = bool(response_lines[8].split(":")[1].strip())
        weight = response_lines[9].split(":")[1].strip()

        # Store responses in the database
        store_responses(date, mood, portfolio, calories, gym, weight)

        print("Responses stored successfully!")
    except Exception as e:
        print(f"Error processing email: {e}")

# Function to connect to Gmail and process emails using Gmail API
def process_emails():
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Create the Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Search for emails with a specific subject (replace with your subject)
    # Define the subject and date range you are looking for
    subject_query = 'subject:"Re: Daily Questionnaire"'
    today = datetime.now().strftime('%Y/%m/%d')
    date_query = f'after:{today}'

    # Combine subject and date queries
    combined_query = f'{subject_query} {date_query}'

    # Example: List all emails in the inbox with the specified subject and from today
    results = service.users().messages().list(userId='me', q=combined_query, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    process_email(service, messages[0]['id'])

