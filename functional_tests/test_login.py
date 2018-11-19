import re

from django.core import mail

from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


TEST_EMAIL = 'crossroadsman@gmail.com'
SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):

    def test_can_get_email_link_to_log_in(self):

        # Alice goes to the awesome superlists site and notices a 'Log in'
        # section in the navbar for the first time.
        # It's telling her to enter her email address, so she does
        self.browser.get(self.live_server_url)
        email_element = self.browser.find_element_by_name('email')
        email_element.send_keys(TEST_EMAIL)
        email_element.send_keys(Keys.ENTER)

        # A message appears telling her that an email has been sent
        # with instructions for logging in
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))

        # She checks her email and finds a message
        # (For now, we can use Django's mail outbox as a proxy for emails
        # that were actually delivered).
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # It has a url link in it
        self.assertIn('Use this link to log in', email.body)
        url_search = re.search(r'https?://.+/.+$',
                               email.body,
                               flags=re.IGNORECASE)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{email.body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # She clicks it
        self.browser.get(url)

        # She is logged in
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Log Out')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)
