from unittest.mock import patch, call

from django.test import TestCase

import accounts.views
from accounts.models import Token


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
        self.assertEqual(from_email, 'noreply@superlists.com')
        self.assertEqual(to_list, ['alice@example.com'])

    @patch('accounts.views.send_mail')
    def test_POST_sends_link_to_login_using_token_uid(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'alice@example.com'
        })
        
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)

    def test_valid_POST_generates_success_message(self):
        # by default `post` returns the immediate HttpResponse (i.e., 
        # the 302 redirect). We can tell it to follow the redirect and
        # then we'll get back the HttpResponse for the ultimate destination
        post_url = '/accounts/send_login_email'
        post_data = {'email': 'alice@example.com'}
        r1 = self.client.post(post_url, post_data)
        print("Default HttpResponse")
        print("--------------------")
        print(r1)
        print(r1.context)
        r2 = self.client.post(post_url, post_data, follow=True)
        print("Follow=True HttpResponse")
        print("------------------------")
        print(r2)
        print(r2.context)

        # (r1 exists only to visualise the difference between default and
        # follow=True)
        message = list(r2.context['messages'])[0]

        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to log in."
        )
        self.assertEqual(message.tags, "success")

    def test_creates_token_associated_with_email(self):
        self.client.post('/accounts/send_login_email', data={
            'email': 'alice@example.com'
        })
        token = Token.objects.first()
        self.assertEqual(token.email, 'alice@example.com')


# We can use patch to apply a mock to an individual test (like we do
# with `test_POST_sends_link_to_login_using_token_uid`) or to a whole
# test class (like we do here).
#
# Note also that here we are mocking a whole module (`django.contrib.auth`,
# which we expect to import in `accounts.views` as `auth`). Mocking a whole 
# module implicitly mocks out all the functions and any other objects 
# contained in that module.
@patch('accounts.views.auth') 
class LoginViewTest(TestCase):

    def test_redirects_to_home_page(self, mock_auth):
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        self.client.get('/accounts/login?token=abcd123')

        # call_args represents the positional and keyword arguments that
        # the mock was called with. It is an object of type `mock.call` 
        # which is essentially a tuple of 
        # (`positional_args`, `keyword_args`) where:
        # - `positional_args` is a tuple and 
        # - `keyword_args` is a dictionary.
        # thus instead of describing expected_args as call(uid='abcd123')
        # we could have used `( (,), {'uid': 'abcd123'} )`
        result_args = mock_auth.authenticate.call_args
        expected_args = call(uid='abcd123')

        self.assertEqual(
            result_args,
            expected_args
        )

    def test_calls_login_with_valid_user(self, mock_auth):
        response = self.client.get('/accounts/login?token=abcd123')

        subject_request = response.wsgi_request
        subject_user = mock_auth.authenticate.return_value
        result_args = mock_auth.login.call_args
        expected_args = call(subject_request,
                             subject_user)

        self.assertEqual(
            result_args,
            expected_args
        )

    def test_doesnt_call_login_if_invalid_user(self, mock_auth):
        mock_auth.authenticate.return_value = None

        self.client.get('/accounts/login?token=abcd123')

        self.assertEqual(
            mock_auth.login.called,
            False
        )
