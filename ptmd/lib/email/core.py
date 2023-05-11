""" This module is responsible for sending the account activation email.

@author: D. Batista (Terazus)
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .utils import get_config
from ptmd.const import ADMIN_EMAIL
from .load_templates import (
    create_confirmation_email_content,
    create_validated_email_content,
    create_validation_mail_content
)


def send_confirmation_mail(username: str, email: str, token: str) -> str:
    """ Send the account activation email to the user.

    @param username: the name of the user
    @param email: the email of the user
    @param token: the token to be used to activate the account
    @return: the message sent to the user
    """
    service: any = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file(get_config()))
    message: MIMEMultipart = build_email_core(title='PTMD - Account activation', email=email)
    body: str = create_confirmation_email_content(username, token)
    message.attach(MIMEText(body, 'html'))
    create_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    service.users().messages().send(userId="me", body=create_message).execute()
    return body


def send_validated_account_mail(username: str, email: str) -> str:
    """ Send the notification to the user that the account is now active.

    @param username: the name of the user
    @param email: the email of the user
    @return: the message sent to the user
    """
    service: any = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file(get_config()))
    message: MIMEMultipart = build_email_core(title='PTMD - Your account is now active', email=email)
    body: str = create_validated_email_content(username)
    message.attach(MIMEText(body, 'html'))
    create_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    service.users().messages().send(userId="me", body=create_message).execute()
    return body


def send_validation_mail(user: object) -> str:
    """ Send the notification to the admin that a user account needs activation.

    @param user: the User class to be used to get the user information
    @return: the message sent to the user
    """
    service: any = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file(get_config()))
    message: MIMEMultipart = build_email_core(title='PTMD - An account needs to be activated', email=ADMIN_EMAIL)
    body: str = create_validation_mail_content(user)
    message.attach(MIMEText(body, 'html'))
    create_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    service.users().messages().send(userId="me", body=create_message).execute()
    return body


def build_email_core(title: str, email: str) -> MIMEMultipart:
    """ Build the core of the email and return a MIMEMultipart object.

    @param title: the title of the email
    @param email: the email of the user
    @return: the core of the email
    """
    message: MIMEMultipart = MIMEMultipart()
    message['Subject'] = title
    message['From'] = ''
    message['To'] = email
    return message
