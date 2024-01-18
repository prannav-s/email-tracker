from processor import process_emails
from sender import send_email
import schedule
import time

# Schedule both email processing and sending
schedule.every().day.at("15:21").do(process_emails)
schedule.every().day.at("15:15").do(send_email)

# send_email()
#cprocess_emails()
# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(1)
