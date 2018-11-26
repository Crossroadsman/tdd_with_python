from unittest.mock import patch

from django.test import TestCase

import accounts.views


class SendLoginEmailViewTest(TestCase):

    def test_redirects_to_home_page(self):
        response = self.client.post(
            '/accounts/send_login_email',
            data={'email': 'alice@example.com'})
        self.assertRedirects(response, '/')

    # @patch takes the name of the object to patch, it then replaces
    # that object with a MagicMock version for the duration of this
    # test.
    # It also passes the mock object as an argument to the test,
    # (we can call this argument anything we like but convention is to
    # use `mock_<name_of_original_object>`)
    @patch('accounts.views.send_mail')
    def test_POST_sends_email_to_specified_address(self, mock_send_mail):

        self.client.post('/accounts/send_login_email', data={
            'email': 'alice@example.com'
        })

        self.assertEqual(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['alice@example.com'])
