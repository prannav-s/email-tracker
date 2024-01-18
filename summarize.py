import sqlite3
from datetime import datetime, timedelta
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os.path


def send_summary():
    # Connect to the SQLite database
    conn = sqlite3.connect('responses.db')
    cursor = conn.cursor()

    # Execute the SQL query
    query = """
SELECT
    AVG(mood) AS avg_mood,
    MAX(portfolio) - MIN(portfolio) AS portfolio_difference,
    AVG(calories) AS avg_calories,
    SUM(gym) AS gym_attendance,
    MAX(weight) - MIN(weight) AS weight_difference
FROM (
    SELECT *
    FROM responses
    ORDER BY id DESC
    LIMIT 7
) AS subquery;
    """
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchall()

    avg_mood = result[0][0]
    portfolio_diff = result[0][1]
    avg_calories = result[0][2]
    gym_attendance = result[0][3]
    weight_difference = result[0][4]


    # Close the database connection
    conn.close()

    sender_email = 'prannav.shankar@gmail.com'
    recipient_email = 'prannav.shankar@gmail.com'
    subject = 'Weekly Questionnaire Summary'
    body = f'''Hi Prannav! I hope you had a good week! Here is your weekly summary:

Average mood: {avg_mood}
Portfolio difference: {portfolio_diff}
Average calories: {avg_calories}
Total gym attendance: {gym_attendance}
Weight difference: {weight_difference}'''

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


