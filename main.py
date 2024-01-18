from processor import process_emails
from sender import send_email
from summarize import send_summary
import schedule
import time

# Schedule both email processing and sending
schedule.every().day.at("20:00").do(send_email)
schedule.every().day.at("23:59").do(process_emails)
schedule.every().sunday.at("23:59").do(send_summary)


# send_email()
#cprocess_emails()
# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(1)
