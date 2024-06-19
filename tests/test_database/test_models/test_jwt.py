from unittest import TestCase
from unittest.mock import MagicMock, patch

from ptmd.database.models.user import User
from ptmd.database.models.jwt import JWT, check_token_valid


class TestJWT(TestCase):

    def test_constructor(self):
        user: User = MagicMock()
        user.return_value.id = 1
        jwt: JWT = JWT(jti='jti', user=user)
        self.assertEqual(jwt.jti, 'jti')
        self.assertEqual(jwt.user, user)

        with patch('ptmd.database.models.jwt.session') as mocked_session:
            mocked_session.query().filter_by().return_value = True
            self.assertFalse(check_token_valid({}, {'jti': '123'}))
