""" Module to load the email templates
"""
from os import path
from typing import Any

from jinja2 import Template

from ptmd.const import SITE_URL
from .const import TEMPLATES_PATH


def create_confirmation_email_content(username: str, token: str) -> str:
    """ Create the content of the confirmation email to be sent to the user.

    :param username: the name of the user
    :param token: the token to be used to activate the account
    :return: the content of the email
    """
    with open(path.join(TEMPLATES_PATH, 'enable_account.html'), 'r') as template_data:
        template: Template = Template(template_data.read())
        return template.render(username=username, url=f'{SITE_URL}/users/enable/{token}')


def create_validated_email_content(username: str) -> str:
    """ Create the content of the email to be sent to the user when his account has been validated by an admin.

    :param username: the name of the user
    :return: the content of the email
    """
    with open(path.join(TEMPLATES_PATH, 'activated_account.html'), 'r') as template_data:
        template: Template = Template(template_data.read())
        return template.render(username=username)


def create_validation_mail_content(user: Any) -> str:
    """ Create the content of the email to be sent to the user.

    :param user: the user account to activate
    :return: the content of the email
    """
    with open(path.join(TEMPLATES_PATH, 'activate_account.html'), 'r') as template_data:
        template: Template = Template(template_data.read())
        return template.render(user=user, site_url=f'{SITE_URL}/api/users/{user.id}/activate')


def create_reset_pwd_mail_content(username: str, token: str) -> str:
    """ Create the content of the email to be sent to the user.

    :param username: the name of the user
    :param token: the token to be used to activate the account
    :return: the content of the email
    """
    with open(path.join(TEMPLATES_PATH, 'reset_password.html'), 'r') as template_data:
        template: Template = Template(template_data.read())
        return template.render(username=username, url=f'{SITE_URL}/users/reset_pwd/{token}')


def create_file_shipped_mail_content(filename: str) -> str:
    """ Create the content of the email to be sent to admins when a file ships.

    :param filename: the name of the file which has been shipped.
    :return: the content of the email
    """
    with open(path.join(TEMPLATES_PATH, 'file_shipped.html'), 'r') as template_data:
        template: Template = Template(template_data.read())
        return template.render(filename=filename)
