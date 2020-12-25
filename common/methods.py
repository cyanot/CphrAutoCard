import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from colorama import init, Fore
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, ConnectionError

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


def send_http_packet(url):
    # requests.packages.urllib3.disable_warnings()
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    headers = {'User-Agent': user_agent}
    url = "http://" + url
    response_html= ""
    # file = open("http_logs.txt","a")
    try:
        response = requests.get(url, headers)
        response_html = response.content.decode()
        return True
    except ReadTimeout:
        print('Read Timeout')
        # file.write(time.asctime(time.localtime(time.time())) + " Read Timeout \n")
        # file.close()
        return False
    except ConnectTimeout:
        print('Connect Timeout')
        # file.write(time.asctime(time.localtime(time.time())) + " Connect Timeout \n")
        # file.close()
        return False
    except HTTPError:
        print('HTTP Error')
        # file.write(time.asctime(time.localtime(time.time())) + " HTTP Error \n")
        # file.close()
        return False
    except ConnectionError:
        print('Connection Error')
        # file.write(time.asctime(time.localtime(time.time())) + " Connection Error \n")
        # file.close()
        return False
