from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database.models.token_blocklist import TokenBlocklist, check_if_token_revoked


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestTokenBlocklist(TestCase):

    def test_token_block_list(self):
        expired_token = TokenBlocklist(jti='123')
        self.assertTrue(expired_token.jti == "123")

        with patch('ptmd.database.models.token_blocklist.session') as mocked_session:
            mocked_session.query().filter_by().return_value = True
            self.assertTrue(check_if_token_revoked({}, {'jti': '123'}))
