""" This module is responsible for sending the account activation email.

@author: D. Batista (Terazus)
"""

from os import path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from jinja2 import Template
from yaml import safe_load

from ptmd.const import SETTINGS_FILE_PATH, SITE_URL


def send_confirmation_mail(username: str, email: str, token: str) -> str:
    """ Send the account activation email to the user.

    @param username: the name of the user
    @param email: the email of the user
    @param token: the token to be used to activate the account
    @return: the message sent to the user
    """
    credentials: Credentials = Credentials.from_authorized_user_file(get_config())
    service: any = build('gmail', 'v1', credentials=credentials)
    message: MIMEMultipart = MIMEMultipart()
    message['Subject'] = 'PTMD - Account Activation'
    message['From'] = ''
    message['To'] = email
    body: str = create_mail_content(username, token)
    message.attach(MIMEText(body, 'html'))
    create_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    service.users().messages().send(userId="me", body=create_message).execute()
    return body


def get_config() -> str:
    """ Get the configuration file for the Google Drive API.

    @return: the path to the credentials file
    """
    with open(SETTINGS_FILE_PATH, 'r') as settings_file:
        settings = safe_load(settings_file)
    return settings['save_credentials_file']


def create_mail_content(username: str, token: str) -> str:
    """ Create the content of the email to be sent to the user.

    @param username: the name of the user
    @param token: the token to be used to activate the account
    @return: the content of the email
    """
    with open(path.join(path.abspath(path.dirname(__file__)), './validate_account.html'), 'r') as template:
        template = Template(template.read())
        return template.render(username=username, url=f'{SITE_URL}/activate/{token}')
