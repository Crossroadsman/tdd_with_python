import time

from django.test import LiveServerTestCase

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
MAX_WAIT = 10  # some values were occasionally expiring when set to 10


"""Tests
   -----
"""
class NewVisitorTest(LiveServerTestCase):

    # setUp and tearDown
    # ------------------
    def setUp(self):
        self.browser = webdriver.Firefox()

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


    # Tests
    # -----
    def test_can_start_a_list_and_retrieve_it_later(self):
        """TODO 20181025: This is a huge test that tests a whole bunch of 
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
        self.assertRegex(bob_list_url, '/list/.+')
        self.assertNotEqual(bob_list_url, alice_list_url)

        # Still no trace of Alice's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)
        
        # - the id (after the /lists/) uniquely identifies her list
        self.fail('Finish the test!')

        # has generated a unique URL for her, together with explanatory text
        # to that effect.
        # She visits the URL: her to-do list is still there.


# --------

if __name__ == '__main__':
    unittest.main()
