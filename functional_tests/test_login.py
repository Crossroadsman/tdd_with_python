import os
import poplib
import time
import re

from django.core import mail

from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):

    # helper methods
    # --------------
    def wait_for_email(self, test_email_to_address, subject):
        if not self.staging_server:  # test server
            email = mail.outbox[0]
            self.assertIn(test_email_to_address, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        else:  # live server
            email_id = None
            start = time.time()
            inbox = poplib.POP3_SSL('mail.gandi.net')
            try:
                inbox.user(test_email_to_address)
                inbox.pass_(os.environ['RECIPIENT_EMAIL_PASSWORD'])
                while time.time() - start < 60:
                    # get 10 newest messages
                    count, _ = inbox.stat()
                    for i in reversed(range(max(1, count - 10), count + 1)):
                        print('getting message', i)
                        _, lines, __ = inbox.retr(i)
                        lines = [l.decode('utf8') for l in lines]
                        print(lines)
                        if f'Subject: {subject}' in lines:
                            email_id = i
                            body = '\n'.join(lines)
                            return body
                    time.sleep(5)
            finally:
                if email_id:
                    inbox.dele(email_id)
                    inbox.quit()


    # tests
    # -----
    def test_can_get_email_link_to_log_in(self):

        # Alice goes to the awesome superlists site and notices a 'Log in'
        # section in the navbar for the first time.
        # It's telling her to enter her email address, so she does
        # (`find_element_by_name` returns the html element with the 
        # specified `name` attribute (i.e., not <email>, but
        # <element name='email'>))
        if self.staging_server:  # Live server
            test_email = os.environ['RECIPIENT_EMAIL_USER']
        else:
            test_email = 'alice@example.com'

        self.browser.get(self.live_server_url)
        email_element = self.browser.find_element_by_name('email')
        email_element.send_keys(test_email)
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
        email_body = self.wait_for_email(test_email, SUBJECT)

        # It has a url link in it
        self.assertIn('Use this link to log in', email_body)
        url_search = re.search(r'https?://.+/.+$',
                               email_body,
                               flags=re.IGNORECASE)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{email_body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # She clicks it
        self.browser.get(url)

        # She is logged in
        self.wait_to_be_logged_in(email=test_email)

        # Now she logs out
        self.browser.find_element_by_link_text('Log Out').click()

        # She is logged out
        self.wait_to_be_logged_out(email=test_email)

