from unittest import skip

from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


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


"""Tests
   -----
"""
class ItemValidationTest(FunctionalTest):

    def test_cannot_add_empty_list_items(self):

        # Alice goes to the home page and accidentally tries to submit an
        # empty list item. She hits Enter on the empty input box.
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)

        # The home page responds with an error message saying that list
        # items cannot be blank.
        # (As originally written, this test could fail, even if the code 
        # works, because this assert will fire before the page has had 
        # time to reload with the new css and error message. Thus we need 
        # an explicit wait)
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ))

        # She tries again with some text for the item, which now works.
        new_item_field = self.browser.find_element_by_id('id_new_item')
        new_item_field.send_keys('Buy milk')
        new_item_field.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # (Now on her list page) Then she forgets the earlier admonition 
        # and again tries to submit an empty list item
        self.browser.find_element_by_id('id_new_item').send_keys(Keys.ENTER)

        # She receives a similar warning from the list page.
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ))

        # She corrects it by filling some text in.
        new_item_field = self.browser.find_element_by_id('id_new_item')
        new_item_field.send_keys('Make tea')
        new_item_field.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')

