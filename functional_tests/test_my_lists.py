from django.conf import settings

from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session


class MyListsTest(FunctionalTest):

    """We already have passing integration tests that validate the whole
    email and login (and implicitly, session-creation) process, thus for 
    our tests of individualised lists we will skip that process and instead
    create a function to generate a pre-authenticated session.
    """
    def create_pre_authenticated_session(self, email):

        # first, create a session (and get its session key)
        if self.staging_server:  # running live server
            session_key = create_session_on_server(self.staging_server,
                                                   email)
        else:  # running local
            session_key = create_pre_authenticated_session(email)

        # next, send a cookie to the client in a HttpResponse.
        # to send a cookie we need the client to visit the domain, and
        # 404 pages load fast so:
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
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

