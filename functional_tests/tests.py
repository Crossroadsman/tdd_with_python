import os
import time
from unittest import skip

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
from selenium.webdriver.common.keys import Keys
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
MAX_WAIT = 10  # can change if tests frequently timeout


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
        time.sleep(1) # give page a moment to load
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        return [row.text for row in rows]

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            row_texts = self.get_table_row_texts()
            try:
                self.assertIn(row_text, row_texts)
            except (AssertionError, WebDriverException) as e:
                # We need both types of error/exception:
                # AssertionError will fire if the table exists but the
                # row isn't in there yet; WebDriverException will fire
                # if the page hasn't loaded
                if time.time() - start_time > MAX_WAIT:
                    raise e
                # time.sleep(0.5)  # move sleep into get_table_row_texts
            else:
                return


"""Tests
   -----
"""
class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_and_retrieve_it_later(self):
        """Test basic functionality: making a list then retrieving it
        later
 
        TODO 20181025: This is a huge test that tests a whole bunch of 
        things. Is this typical for functional tests?

        A 20181101: It seems necessary for a functional (=integration)
        test to be long and include a bunch of things since the single
        piece of functionality we are testing is the user's ability to
        complete a task, which comprises a sequence of user interactions.
        """

        # Alice has heard about a cool new online to-do app. She goes to 
        # check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        target_text = 'To-Do'
        self.assertIn(target_text, self.browser.title)
        
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn(target_text, header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # She types "Buy peacock feathers" into a text box
        inputbox.send_keys('Buy peacock feathers')

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly"
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # Satisfied she goes back to sleep.

    def test_multiple_users_can_start_lists_with_unique_urls(self):
        # Alice starts a new to-do list
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # Alice wants the site to remember her list. She sees that:
        # - the site has generated a url with a logical structure beginning
        #   with /lists/
        alice_list_url = self.browser.current_url
        self.assertRegex(alice_list_url, '/lists/.+')

        # In the meantime, Bob accesses the site.
        # (We will use a new browser session to ensure that no information
        # from Alice's session is coming through, e.g., from cookies)
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Bob visits the home page, there is no sign of Alice's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Bob starts a new list by entering a new item. His is less
        # interesting than Alice
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Bob gets his own unique URL of the same form
        bob_list_url = self.browser.current_url
        self.assertRegex(bob_list_url, '/lists/.+')
        self.assertNotEqual(bob_list_url, alice_list_url)

        # Still no trace of Alice's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)
        
        # - the id (after the /lists/) uniquely identifies her list
        # (the self.assertNotEqual(bob_list_url, alice_list_url) is as
        # close to a test of uniqueness as is feasible right now)


class LayoutAndStylingTest(FunctionalTest):

    def test_layout_and_styling(self):
        """Ensure that critical elements of layout are rendered"""
        # Alice goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centred
        # (we're checking that the middle of the input box is approximately
        # in the centre of the window (of specified size))
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10  # 10 is good delta to cover weirdness like scrollbars
        )

        # She starts a new list and sees the input is centred there, too
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')

        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )


class ItemValidationTest(FunctionalTest):

    @skip  # we're not ready to run this test yet.
    def test_cannot_add_empty_list_items(self):

        # Alice goes to the home page and accidentally tries to submit an
        # empty list item. She hits Enter on the empty input box.
        self.fail('write me!')

        # The home page responds with an error message saying that list
        # items cannot be blank.

        # She tries again with some text for the item, which now works.

        # Then she forgets the earlier admonition and again tries to submit
        # an empty list item.

        # She receives a similar warning on the list page.

        # She corrects it by filling some text in.


# --------

if __name__ == '__main__':
    unittest.main()
