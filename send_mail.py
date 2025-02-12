import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email credentials
EMAIL_ADDRESS = "email"
EMAIL_PASSWORD = "password"

def send_email(to_address, subject, message):
    try:
        # Set up the server
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Create the email
        email = MIMEMultipart()
        email['From'] = EMAIL_ADDRESS
        email['To'] = to_address
        email['Subject'] = subject
        email.attach(MIMEText(message, 'plain'))
        
        # Send the email
        server.send_message(email)
        server.quit()
        print(f"Email sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_account_creation_email(to_address, first_name, account_number):
    subject = "Account Created Successfully"
    message = f"Dear {first_name},\n\nYour account has been created successfully. Your account number is {account_number}.\n\nThank you for choosing our bank."
    send_email(to_address, subject, message)

def send_login_notification_email(to_address, first_name):
    subject = "Login Notification"
    message = f"Dear {first_name},\n\nYou have successfully logged in to your account.\n\nThank you for choosing our bank."
    send_email(to_address, subject, message)

def send_transaction_email(to_address, first_name, amount, recipient_name):
    subject = "Transaction Successful"
    message = f"Dear {first_name},\n\nYou have successfully sent ${amount:.2f} to {recipient_name}.\n\nThank you for choosing our bank."
    send_email(to_address, subject, message)
