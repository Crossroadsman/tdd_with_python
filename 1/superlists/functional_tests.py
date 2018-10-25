from selenium import webdriver
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
browser = webdriver.Firefox()

# Alice has heard about a cool new online to-do app. She goes to check
# out its homepage
browser.get('http://localhost:8000')

# She notices the page title and header mention to-do lists
assert 'To-Do' in browser.title

# She is invited to enter a to-do item straight away

# She types "Buy peacock feathers" into a text box

# When she hits enter, the page updates, and now the page lists
# "1: Buy peacock feathers" as an item in a to-do list

# There is still a text box inviting her to add another item. She
# enters "Use peacock feathers to make a fly"

# The page updates again, and now shows both items on her list

# Alice wants the site to remember he list. She sees that the site
# has generated a unique URL for her, together with explanatory text
# to that effect.

# She visits the URL: her to-do list is still there.

# Satisfied she goes back to sleep.
browser.quit()
