from unittest import TestCase

from ptmd.const import SITE_URL
from ptmd.database.models import User, Organisation
from ptmd.lib.email.load_templates import (
    create_validation_mail_content, create_validated_email_content, create_confirmation_email_content
)


class TestTemplateLoaders(TestCase):

    def test_confirmation_email(self):
        data = create_confirmation_email_content('USERNAME', 'TOKEN')
        self.assertIn('USERNAME', data)
        self.assertIn('TOKEN', data)
        self.assertIn(f'{SITE_URL}/users/enable/TOKEN', data)

    def test_validated_email(self):
        data = create_validated_email_content('USERNAME')
        self.assertIn('USERNAME', data)

    def test_create_validation_mail_content(self):
        organisation = Organisation(name='ORGANISATION NAME')
        user = User(username='USERNAME', password='!Str0?nkPassw0rd', email='EMAIL', role='admin',
                    organisation_id=organisation.organisation_id)
        data = create_validation_mail_content(user)
        self.assertIn('USERNAME', data)
        self.assertIn('EMAIL', data)
        self.assertIn(f'{SITE_URL}/api/users/{user.id}/activate', data)
