import os
import time

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
MAX_WAIT = 3  # can change if tests frequently timeout
WAIT_TICK = 0.1  # change if tests frequently timeout


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
        staging_server = os.environ.get('SUPERLISTS_STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

    def tearDown(self):
        self.browser.quit()

    # helper methods
    # --------------
    def get_table_row_texts(self):

        # we were getting selenium StaleElementException with the sleep
        # in the original location. This might be because on the first
        # iteration of the loop, the page is still loading (longer now
        # because of redirect after POST). Thus between id_list_table
        # being assigned to table and querying table for `tr` elements
        # the trs had gone stale.
        # Thus we put a sleep before we assign to table so that when
        # we do get `id_list_table` it is from the fully loaded page
        # and so not stale when we go back to look for `tr` elements
        # This has now worked at least once since moving the sleep
        # but Internet weather might cause a failure in the future if
        # load time is particularly slow. At that time we could consider
        # raising the sleep time.
        time.sleep(WAIT_TICK) # give page a moment to load
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        return [row.text for row in rows]

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                row_texts = self.get_table_row_texts()
            # WebDriverException will fire if the page hasn't loaded
            except WebDriverException as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
            else:
                try:
                    self.assertIn(row_text, row_texts)
                # AssertionError will fire if the table exists but the
                # row isn't present (yet).
                except AssertionError as e:
                    if time.time() - start_time > MAX_WAIT:
                        raise e
                else:
                    return

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                # time.sleep(1)
                return fn()
            # WebDriverException will fire if the page hasn't reloaded
            # AssertionError will fire if the page has started to load
            # but hasn't yet loaded the specified value, or if the
            # page has fully loaded but the specified value doesn't exist
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(WAIT_TICK)

    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')

