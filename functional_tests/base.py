import os
import time

from selenium.webdriver.common.keys import Keys

from .server_tools import reset_database


"""django.test.LiveServerTestCase
               ------------------
https://docs.djangoproject.com/en/2.1/topics/testing/tools/#django.test.LiveServerTestCase
- launches a live Django server in the background on setUp and shuts it
  down on tearDown (thus each test gets a fresh server)
- It provides certain APIs to enable communication with the server, e.g.,
  live_server_url to get the server's url.
- This allows the use of functional tests with, e.g., Selenium to execute
  a series of functional tests inside a browser.

django.contrib.staticfiles.testing.StaticLiveServerTestCase
                                   ------------------------
https://docs.djangoproject.com/en/2.1/howto/static-files/#staticfiles-testing-support
- This is a subclass of Django's LiveServerTestCase
- It adds the ability to serve assets during development in much the same
  way as the Django dev server can when DEBUG=True
- This lets us test static assets without needing to run `collectstatic`
"""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
"""Functional Tests vs Unit Tests:
   ------------------------------
See also:
https://stackoverflow.com/questions/2741832/unit-tests-vs-functional-tests

Functional tests are written from the user's perspective (cf unit tests
from programmer's perspective). Confirm that the system does what users
expect (cf unit tests confirm that the system does what the programmer
intended). Consider the difference when building a house between the 
home inspector (unit tests) and the new homeowner (functional tests).
The former checks that the electrics and plumbing function correctly and
safely, while the latter checks that the system is livable.

Put another way, unit tests confirm the code is doing things right; 
functional tests confirm the code is doing the right things.
"""

"""Installation Notes
   ------------------
To enable firefox to run on a headless Ubuntu server we need to:
- install geckodriver (mozilla/geckodriver on github)
  ```console
  # <EITHER>
  wget <url> -O geckodriver.tar.gz
  # <OR>
  curl -L <url> -o geckodriver.tar.gz
  # <THEN>
  mkdir ~/bin
  tar -xvf geckodriver.tar.gz -C ~/bin
  # <THEN MAYBE (SEE COMMENTS)>
  chmod +x ~/bin/geckodriver  # if doesn't already have execute permission
  echo PATH=$PATH:~/bin >> ~/.profile  # if ~/bin isn't already in path
  . ~/.profile
  ```
- install firefox
- install xvfb (the X windows virtual framebuffer)
- Run xvfb in the background (of the session running the tests)
  ```console
  Xvfb :10 -ac &
  ```
- set the DISPLAY variable
  ```console
  export DISPLAY=:10
  ```
"""


"""Constants
   ---------
"""
MAX_WAIT = 3  # can change if tests frequently timeout (initial 3)
WAIT_TICK = 0.5  # change if tests frequently timeout (inital 0.5)


"""Base Test Class
   ---------------
"""
class FunctionalTest(StaticLiveServerTestCase):

    # setUp and tearDown
    # ------------------
    def setUp(self):
        self.browser = webdriver.Firefox()
        # the following lets us choose (by setting an environment variable)
        # whether we want a LiveServerTestCase-provided server instance or
        # if we want to use a real server
        self.staging_server = os.environ.get('SUPERLISTS_STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = 'http://' + self.staging_server
            reset_database(self.staging_server)

    def tearDown(self):
        self.browser.quit()

    # decorator methods
    # -----------------
    def wait(fn):
        def modified_fn(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (AssertionError, WebDriverException) as e:
                    if time.time() - start_time > MAX_WAIT:
                        raise e
                    time.sleep(WAIT_TICK)
        return modified_fn

    # helper methods
    # --------------
    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_to_be_logged_in(self, email):
        # we know that if the page has  a `Log Out` link, the user must be
        # logged in.
        self.browser.find_element_by_link_text('Log Out')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    def wait_to_be_logged_out(self, email):
        # we know that if there is an element with a name attribute of
        # 'email' that the user is not logged in.
        self.browser.find_element_by_name('email')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)

    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')

    def add_list_item(self, item_text):
        num_rows_before = len(self.browser.find_elements_by_css_selector(
            '#id_list_table tr'
        ))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        new_item_number = num_rows_before + 1
        self.wait_for_row_in_list_table(
            f'{new_item_number}: {item_text}'
        )

    

