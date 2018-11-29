from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    SESSION_KEY,
    get_user_model)
from django.contrib.sessions.backends.db import SessionStore

from .base import FunctionalTest

User = get_user_model()


class MyListsTest(FunctionalTest):

    """We already have passing integration tests that validate the whole
    email and login (and implicitly, session-creation) process, thus for 
    our tests of individualised lists we will skip that process and instead
    create a function to generate a pre-authenticated session.
    """
    def create_pre_authenticated_session(self, email):

        # first, create a user
        user = User.objects.create(email=email)
 
        # second, create a session object in the database (by default
        # Django stores its sessions in the DB). The session's
        # SESSION_KEY is the user object's pk.
        # The session also stores information to lookup which authentication
        # backend was used to authenticate th user. Hence the
        # BACKEND_SESSION_KEY
        # (if this stops working and needs a hash session key, check the
        # following gist:
        # https://gist.github.com/dbrgn/bae5329e17d2801a041e
        # )
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()

        # third, send a cookie in a HttpResponse.
        # to send a cookie we need the client to visit the domain, and
        # 404 pages load fast so:
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
        ))

    def test_logged_in_users_lists_are_saved(self):
        email = 'alice@example.com'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Alice is a logged-in user
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)

