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
        self.fail('write me!')

        # The home page responds with an error message saying that list
        # items cannot be blank.

        # She tries again with some text for the item, which now works.

        # Then she forgets the earlier admonition and again tries to submit
        # an empty list item.

        # She receives a similar warning on the list page.

        # She corrects it by filling some text in.

