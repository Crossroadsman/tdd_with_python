class MyListsPage():

    def __init__(self, test):
        self.test = test

    def get_gethelp_link(self):
        return self.test.browser.find_element_by_link_text('Get help')

    def get_mylists_link(self):
        return self.test.browser.find_element_by_link_text('My Lists')

    def get_logout_link(self):
        return self.test.browser.find_element_by_link_text('Log Out')

    def get_list_link(self, list_name):
        return self.test.browser.find_element_by_link_text(list_name)

    def go_to_my_lists_page(self):
        self.test.browser.get(self.test.live_server_url)
        self.get_mylists_link().click()
        self.test.wait_for(lambda: self.test.assertEqual(
            self.test.browser.find_element_by_tag_name('h1').text,
            'My Lists'
        ))
        return self

