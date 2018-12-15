from selenium import webdriver

from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage


class SharingTest(FunctionalTest):

    # Helper Methods
    # --------------
    @staticmethod
    def quit_if_possible(browser):

        # In the Sharing FTs we'll have multiple browsers open at once.
        # Only one of them can be the test's `self.browser` at the time
        # tearDown is called.
        # This function will end up being run after tearDown, so one of
        # the browsers will already have been closed by tearDown. By
        # using try/except here, we don't have to worry about which
        # browser instance is associated with `self.browser` when the test
        # finishes, instead we can just use this function with all the 
        # browser instances loaded during the test.
        try:
            browser.quit()
        except:
            pass

    # Tests
    # -----
    def test_can_share_a_list_with_other_user(self):

        # Alice is a logged-in user
        self.create_pre_authenticated_session('alice@example.com')
        alice_browser = self.browser
        
        # unittest.TestCase.addCleanup(fn, *args, **kwargs)
        # (https://docs.python.org/3/library/unittest.html#unittest.TestCase.addCleanup)
        # adds `fn` to be called after `tearDown()` to cleanup resources
        # used during the test. The value of adding clean up code using
        # addCleanup instead of tearDown is that addCleanup functions
        # will be called even setUp fails.
        self.addCleanup(lambda: self.quit_if_possible(alice_browser))

        # Her friend, Charon, is also hanging out on the lists site
        charon_browser = webdriver.Firefox()
        self.addCleanup(lambda: self.quit_if_possible(charon_browser))
        self.browser = charon_browser
        self.create_pre_authenticated_session('charon@example.com')

        # Alice goes to the home page and starts a list
        self.browser = alice_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Get help')

        # She notices a 'share this list' option
        share_box = list_page.get_share_box()

        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

        # She shares her list with Charon
        list_page.share_list_with('charon@example.com')

        # She observes that the page has been updated to say that it's
        # shared with Charon.
        list_page.wait_for_sharee_in_sharees_list('charon@example.com')

        # Charon now goes to the lists page with his browser
        self.browser = charon_browser
        my_lists_page = MyListsPage(self)
        my_lists_page.go_to_my_lists_page()

        # He sees Alice's list in there:
        my_lists_page.get_list_link('Get help').click()

        # He is then taken to the list page for Alice's list. He can
        # see that the list belongs to Alice
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            'alice@example.com'
        ))

        # He adds an item to the list
        list_page.add_list_item('Hi Alice!')

        # When Alice refreshes the page, she sees Charon's addition
        self.browser = alice_browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table('Hi Alice!', 2)
