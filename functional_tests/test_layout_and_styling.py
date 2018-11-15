from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


"""Installation Notes
   ------------------
see base.py
"""


"""Tests
   -----
"""
class LayoutAndStylingTest(FunctionalTest):

    def test_layout_and_styling(self):
        """Ensure that critical elements of layout are rendered"""
        # Alice goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centred
        # (we're checking that the middle of the input box is approximately
        # in the centre of the window (of specified size))
        inputbox = self.get_item_input_box()
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10  # 10 is good delta to cover weirdness like scrollbars
        )

        # She starts a new list and sees the input is centred there, too
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')

        inputbox = self.get_item_input_box()
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

