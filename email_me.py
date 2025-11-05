import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_txt_file(txt_file_path, recipient_email, sender_email, sender_password, 
                  smtp_server='smtp.gmail.com', smtp_port=587):
    """
    Send a .txt file via email.
    
    Args:
        txt_file_path: Path to the .txt file to send
        recipient_email: Email address to send to
        sender_email: Your email address
        sender_password: Your email password or app-specific password
        smtp_server: SMTP server address (default: Gmail)
        smtp_port: SMTP port (default: 587 for TLS)
    """
    
    # Check if file exists
    if not os.path.exists(txt_file_path):
        raise FileNotFoundError(f"File not found: {txt_file_path}")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Text File: {os.path.basename(txt_file_path)}"
    
    # Add body text
    body = f"Attached is the file: {os.path.basename(txt_file_path)}"
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the file
    with open(txt_file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {os.path.basename(txt_file_path)}'
    )
    msg.attach(part)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

# Example usage
if __name__ == "__main__":
    # Configure these variables
    FILE_PATH = "example.txt"  # Path to your .txt file
    YOUR_EMAIL = "your.email@gmail.com"  # Your email
    YOUR_PASSWORD = "your_app_password"  # App-specific password
    
    # Send to yourself
    send_txt_file(
        txt_file_path=FILE_PATH,
        recipient_email=YOUR_EMAIL,
        sender_email=YOUR_EMAIL,
        sender_password=YOUR_PASSWORD
    )