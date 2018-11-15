from unittest import skip

from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


"""Installation Notes
   ------------------
see base.py
"""

"""Tests
   -----
"""
class ItemValidationTest(FunctionalTest):

    # helper methods
    # --------------
    def get_error_element(self):
        return self.browser.find_element_by_css_selector('.has-error')

    # tests
    # -----
    def test_cannot_add_empty_list_items(self):

        # Alice goes to the home page and accidentally tries to submit an
        # empty list item. She hits Enter on the empty input box.
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)

        # The browser intercepts the request (the `required` attribute
        # was added to the HTML input), and does not load the list page
        # (The `:invalid` CSS pseudoselector is applied by the browser not
        # by our CSS)
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # She starts typing some text for the new item and the error 
        # disappears
        new_item_field = self.get_item_input_box()
        new_item_field.send_keys('Buy milk')
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:valid'
        ))

        # then she can submit it successfully
        new_item_field.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # (Now on her list page) Then she forgets the earlier admonition 
        # and again tries to submit an empty list item
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Again the browser will not comply
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:invalid'
        ))

        # She corrects it by filling some text in.
        new_item_field = self.get_item_input_box()
        new_item_field.send_keys('Make tea')
        self.wait_for(lambda: self.browser.find_elements_by_css_selector(
            '#id_text:valid'
        ))
        new_item_field.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')

    def test_cannot_add_duplicate_items(self):

        # Alice goes to the home page and starts a new list
        self.browser.get(self.live_server_url)
        input_text = 'Buy wellies'
        input_box = self.get_item_input_box()
        input_box.send_keys(input_text)
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(f'1: {input_text}')

        # She accidentally tries to enter a duplicate item
        input_box = self.get_item_input_box()
        input_box.send_keys(input_text)
        input_box.send_keys(Keys.ENTER)

        # She sees a helpful error message
        self.wait_for(lambda: self.assertEqual(
            self.get_error_element().text,
            "You've already got this in your list"
        ))

    def test_error_messages_are_cleared_on_input(self):

        # Alice starts a list and causes a validation error
        self.browser.get(self.live_server_url)
        item_text = 'Banter too thick'
        input_box = self.get_item_input_box()
        input_box.send_keys(item_text)
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(f'1: {item_text}')

        input_box = self.get_item_input_box()
        input_box.send_keys(item_text)
        input_box.send_keys(Keys.ENTER)
        self.wait_for(lambda: self.assertTrue(
            # (we have to use .is_displayed() instead of just checking that
            # the item appears in the DOM as before because we are now
            # starting to hide elements)
            self.get_error_element().is_displayed()
        ))

        # She starts typing in the input box to clear the error
        input_box = self.get_item_input_box()
        input_box.send_keys('a')

        # She is pleased to see that the error message disappears
        self.wait_for(lambda: self.assertFalse(
            self.get_error_element().is_displayed()
        ))

