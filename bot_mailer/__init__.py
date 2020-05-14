import configparser
import smtplib
import ssl

config = configparser.ConfigParser()
config.read('config.ini')

port = 465  # For SSL
password = config['Mail']['pass']
email = config['Mail']['mail']
recepient = config['Mail']['notifyTo']


def send_email(message):
    # Create a secure SSL context
    context = ssl.create_default_context()
    test = """New Appointment from Bot- check callendar"""

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        server.sendmail(email, recepient, test)


if __name__ == '__main__':
    send_email("hello")
