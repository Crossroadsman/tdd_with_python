from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token
import accounts

User = get_user_model()


class AuthenticateTest(TestCase):

    """Note that the book doesn't use the required parameter `request`
    when calling `authenticate` (see the documentation for the
    `authenticate` method for more details). This means we have to figure
    out for ourselves the best way to conjure a request object and pass
    it through to `authenticate`.

    We'll start by just passing None, since this is the easiest, and
    testing the `authenticate()` method in isolation shouldn't depend
    on a particular request. We know from the Django docs that
    `authenticate` should be able to expect None as a value for `request`
    so it's reasonable to think this might work.

    If we need to get more sophisticated, we can use `RequestFactory`
    see:
    https://docs.djangoproject.com/en/2.1/topics/testing/advanced/#the-request-factory
    """
    def setUp(self):
        self.request = None

    def test_invalid_token_returns_None(self):
        result = PasswordlessAuthenticationBackend().authenticate(
            request=self.request,
            uid='no-such-token'
        )
        self.assertIsNone(result)

    def test_valid_token_returns_new_user_if_no_email_associated(self):
        email = 'alice@example.com'
        #before
        with self.assertRaises(accounts.models.ListUser.DoesNotExist):
            User.objects.get(email=email)

        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            request=self.request,
            uid=token.uid
        )

        #after
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)

    def test_valid_token_returns_existing_user_if_email_associated(self):
        email = 'alice@example.com'
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            request=self.request,
            uid=token.uid
        )
        self.assertEqual(user, existing_user)


class GetUserTest(TestCase):

    def test_returns_user_if_valid_email(self):
        User.objects.create(email='another@example.com')
        target_user = User.objects.create(email='alice@example.com')

        found_user = PasswordlessAuthenticationBackend().get_user(
            'alice@example.com'
        )

        self.assertEqual(found_user, target_user)

    def test_returns_None_if_invalid_email(self):
        User.objects.create(email='wronguser@example.com')

        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user(
                'alice@example.com'
            )
        )
