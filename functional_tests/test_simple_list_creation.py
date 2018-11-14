from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


"""Installation Notes
   ------------------
see base.py
"""


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
        inputbox = self.get_item_input_box()
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
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # Satisfied she goes back to sleep.

    def test_multiple_users_can_start_lists_with_unique_urls(self):
        # Alice starts a new to-do list
        self.browser.get(self.live_server_url)
        inputbox = self.get_item_input_box()
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
        inputbox = self.get_item_input_box()
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

