# Send email ----------------------------------------------------
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "An email with attachment from Python"
body = "Test - This is an email with attachment sent from Python"
sender_email = "reports@example.com"
receiver_email = "user@example.com"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# Add body to email
message.attach(MIMEText(body, "plain"))

# for a_file in files:
#     attachment = open(a_file, 'rb')
#     file_name = os.path.basename(a_file)
#     part = MIMEBase('application','octet-stream')
#     part.set_payload(attachment.read())
#     part.add_header('Content-Disposition',
#                     'attachment',
#                     filename=file_name)
#     encoders.encode_base64(part)
#     message.attach(part)

# Encode file in ASCII characters to send by email    
# encoders.encode_base64(part)

# Add attachment to message and convert message to string
text = message.as_string()

# Log in to server using secure context and send email
with smtplib.SMTP('smtp.example.local', 25) as server:
    # server.login(sender_email, password) - prec
    server.sendmail(sender_email, receiver_email, text)