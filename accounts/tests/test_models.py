from django.test import TestCase
from django.contrib.auth import get_user_model

# NOTE: we don't need to import accounts.models.User because, as it has
# the role of Project-wide user, we interact with it through
# django.contrib.auth.get_user_model() or 
# django.conf.AUTH_USER_MODEL
from accounts.models import Token


User = get_user_model()


class UserModelTest(TestCase):

    def test_user_is_valid_with_email_only(self):
        user = User(email='a@b.com')
        user.full_clean()  # should not raise

    def test_email_is_primary_key(self):

        # NOTE: we've made email the primary key mostly as demonstration
        # of how to implement a custom PK instead of letting Django
        # autogenerate one. In real-life, email is a bad choice of PK
        # because a) people might change their email but you don't want
        # to change the PK value for an existing record and b) it's
        # reasonable to expect that there might be a time when you have
        # more than one user sharing an email address.
        user = User(email='a@b.com')
        self.assertEqual(user.pk, 'a@b.com')


class TokenModelTest(TestCase):

    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email='a@b.com')
        token2 = Token.objects.create(email='a@b.com')
        self.assertNotEqual(token1.uid, token2.uid)
