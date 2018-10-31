from django.test import TestCase

class SmokeTest(TestCase):
    # This is a deliberately silly failing test to verify that the 
    # test runner is actually seeing this TestCase
    # (the django test runner is invoked using
    #     $ python3 manage.py test
    # )
    def test_bad_maths(self):
        self.assertEqual(1 + 1, 3)
