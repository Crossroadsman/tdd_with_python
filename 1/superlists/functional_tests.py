import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
- Run xvfb in the background
```console
Xvfb :10 -ac &
```
- set the DISPLAY variable
```console
export DISPLAY=:10
```
"""

"""Tests
   -----
"""
class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

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
        self.browser.get('http://localhost:8000')

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
        time.sleep(1)  # seconds

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn('1: Buy peacock feathers', [row.text for row in rows])

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly"
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # The page updates again, and now shows both items on her list
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        row_texts = [row.text for row in rows]
        self.assertIn('1: Buy peacock feathers', row_texts)
        self.assertIn('2: Use peacock feathers to make a fly')

        # Alice wants the site to remember he list. She sees that the site
        # has generated a unique URL for her, together with explanatory text
        # to that effect.
        self.fail('Finish the test!')

        # She visits the URL: her to-do list is still there.

        # Satisfied she goes back to sleep.

# --------

if __name__ == '__main__':
    unittest.main()
