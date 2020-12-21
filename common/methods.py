import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from colorama import init, Fore
init(autoreset=True)


def send_email(img_file_path, subject, config):
    host = config.get("mail", "host")
    port = config.get('mail', 'port')

    receiver = config.get('mail', 'receiver')
    sender = config.get('mail', 'sender')

    username = config.get('mail', 'username')
    password = config.get('mail', 'password')

    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receiver
    content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')
    message.attach(content)
    file = open(img_file_path, "rb")
    img_data = file.read()
    file.close()
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    message.attach(img)

    try:
        server = smtplib.SMTP_SSL(host, port)
        server.login(username, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        print(Fore.MAGENTA + "发送邮件成功")
    except smtplib.SMTPException as e:
        # print("error")
        print(e)
