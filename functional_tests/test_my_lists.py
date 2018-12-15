from django.conf import settings

from .base import FunctionalTest
from .my_lists_page import MyListsPage


class MyListsTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved(self):

        # Alice is a logged-in user
        email = 'alice@example.com'
        self.create_pre_authenticated_session(email)

        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # She notices a "My lists" link, for the first time, and clicks it
        my_lists_page = MyListsPage(self).go_to_my_lists_page()

        # She sees that her new list is in there, named according to its
        # first list item
        self.wait_for(
            lambda: self.browser.find_element_by_link_text(
                'Reticulate splines'
            )
        )

        # She clicks the link represented by her first list item
        my_lists_page.get_list_link('Reticulate splines').click()

        # And notices that it takes her to the full list
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url,
                                     first_list_url)
        )
        
        # She decides to start another list (just to see if she can keep
        # two lists simultaneously)
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        second_list_url = self.browser.current_url

        # Now, under 'my lists', her new list appears
        my_lists_page = MyListsPage(self).go_to_my_lists_page()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Click cows')
        )
        my_lists_page.get_list_link('Click cows').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url,
                                     second_list_url)
        )

        # She logs out. The 'My Lists' option disappears
        my_lists_page.get_logout_link().click()
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_elements_by_link_text('My Lists'),
                []
            )
        )

