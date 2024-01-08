import unittest

from selenium.webdriver.remote.webelement import WebElement

from bot import InstaBot, POST_ID, COMMENTS_HTML_ELEMENT_XPATH
from browser import driver


class TestBot(unittest.TestCase):

    bot = InstaBot(driver=driver)

    def test__get_all_published_comments(self):
        """ Always return a list of dict """
        comments = self.bot.get_all_published_comments()
        self.assertIsInstance(comments, list)

    def test__browse_comments_box_web_element(self):
        """ Get comment box : get a valid web element """

        self.assertIsInstance(
            self.bot.get_comments_box_web_element(xpath=COMMENTS_HTML_ELEMENT_XPATH),
            WebElement
        )
    
    def test__browse_comments_box_html_element(self):
        """ Get comments HTML element box (div) """

        source = self.bot.get_comments_source(post_id=POST_ID)
        self.assertIsInstance(source, str)
        self.assertTrue("<div>" in source)
    

if __name__ == "__main__":
    unittest.main()


