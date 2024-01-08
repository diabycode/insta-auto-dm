import time
import json
from pathlib import Path
import datetime
import sys

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from browser import driver


COMMENTS_FILE_PATH = Path(__file__).parent / "comments.json"
AUTH_ACCOUNT_FILE_PATH = Path(__file__).parent / "account.json"
KEYWORDS_FILE_PATH = Path(__file__).parent / "keywords"
AUTO_DM_MESSAGE_FILE_PATH = Path(__file__).parent / "message"
POST_ID_FILE_PATH = Path(__file__).parent / "post"
ACCOUNT_DATA_FILE_PATH = Path(__file__).parent / "account.json"

COMMENTS_HTML_ELEMENT_XPATH = "//div[contains(@class,'x5yr21d xw2csxc x1odjw0f x1n2onr6')]"

with POST_ID_FILE_PATH.open("r") as f:
    POST_ID = (f.read()).strip("\n").strip(" ")

BASE_URL = "https://www.instagram.com/"
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class InstaBot:

    def __init__(self, driver) -> None:
        self.driver = driver
        self._init_settings()
        self.login(self.username, self.password)

    def _init_settings(self):
        if not Path(ACCOUNT_DATA_FILE_PATH).exists():
            with Path(ACCOUNT_DATA_FILE_PATH).open("w", encoding="utf-8") as f:
                json.dump({
                    "username": "",
                    "password": ""
                }, f, indent=4)
        print("'account.json' file .....ok")
        
        if not Path(COMMENTS_FILE_PATH).exists():
            with Path(COMMENTS_FILE_PATH).open("w", encoding="utf-8") as f:
                json.dump([], f)
        print("'comments.json' file .....ok\n")

        print("!! Make sure you have everything set up. [keywords, message, post]")

        with open(ACCOUNT_DATA_FILE_PATH, "r") as f:
            account = json.load(f)

        USERNAME = account.get("username")
        if USERNAME == "":
            print("No account configured in 'account.json' !")
            driver.quit()
            sys.exit(1)
        
        PASSWORD = account["password"]
        self.username = USERNAME
        self.password = PASSWORD

    def go(self):
        print(f"User '{self.username}' is logged in.")
        input("Press ENTER to continue...")

        self._inspect_post()

    def get_all_published_comments(self):
        source = self.get_comments_source(post_id=POST_ID)
        return self._parse_comments_through_source(source=source)

    def _inspect_post(self):
        comments = self.get_all_published_comments()
        self._write_comments(comments)

        while True:
            print("Waiting for new comments...")

            comments_source_code = self.get_comments_source(post_id=POST_ID)
            if self._is_new_comments(source=comments_source_code):
                print("New comment(s) detected !!!!!")

                new_comments: list = self._get_new_comments(source_code=comments_source_code)
                self._dm_comments(new_comments)

                new_comments_list_to_save: list = self._read_comments()
                new_comments_list_to_save.extend(new_comments)
                new_comments_list_to_save.sort(key=lambda x: datetime.datetime.strptime(x["published_date"], DATE_TIME_FORMAT))
                self._write_comments(new_comments_list_to_save)
                print("end!")

    @property
    def _is_authenticated(self):
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(1.5)
        if "login" in self.driver.current_url:
            return False
        return True

    def login(self, username, password):
        self.driver.get("https://www.instagram.com/")
        time.sleep(2)

        # connection
        self.driver.find_element(By.XPATH, "//*[@id=\"loginForm\"]/div/div[1]/div/label/input").send_keys(username)
        time.sleep(1.5)
        self.driver.find_element(By.XPATH, "//*[@id=\"loginForm\"]/div/div[2]/div/label/input").send_keys(password)
        time.sleep(1.5)
        self.driver.find_element(By.XPATH, "//*[@id=\"loginForm\"]/div/div[3]/button").click()
        time.sleep(5)

        if self._is_authenticated:
            return 

        t = 0
        while True:
            if t > 2:
                self.login(username, password)
                print("Not logged ! reconnecting...")

            if self._is_authenticated:
                return
            
            t += 1

    def send_message(self, message, user):
        """ send message to a specific user """

        self.driver.get(BASE_URL + user) # go to user profile
        time.sleep(5)

        t = 0 # attempts

        # Trying to find contact button
        while True:
            if t > 2:
                print(f"Something went wrong when trying to contact '{user}'")
                return

            try:
                contact_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1i64zmx x1n2onr6 x6ikm8r x10wlt62 x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1')]")
            except NoSuchElementException:
                t += 1
            else:
                contact_btn.click()
                time.sleep(5)
                t = 0
                break

        # Trying to get message input and fill it
        while True:
            if t > 2:
                print(f"Something went wrong when trying to contact '{user}'")
                return

            try:
                message_input = self.driver.find_element(By.XPATH, "//p[contains(@class, 'xat24cr xdj266r')]")
            except NoSuchElementException:
                t += 1
            else:
                message_input.click()
                message_input.send_keys(message)
                time.sleep(2)
                t = 0
                break

        # trying to find send button and click on it
        while True:
            if t > 2:
                print(f"Something went wrong when trying to contact '{user}'")
                return

            try:
                send_btn = self.driver.find_element(By.XPATH, "//div[contains(@class, 'x1i10hfl xjqpnuy xa49m3k xqeqjp1 x2hbi6w xdl72j9 x2lah0s xe8uvvx xdj266r xat24cr x1mh8g0r x2lwn1j xeuugli x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x1lku1pv x1a2a7pz x6s0dn4 xjyslct x1ejq31n xd10rxx x1sy0etr x17r0tee x9f619 x1ypdohk x1f6kntn xwhw2v2 xl56j7k x17ydfre x2b8uid xlyipyv x87ps6o x14atkfc xcdnw81 x1i0vuye xjbqb8w xm3z3ea x1x8b98j x131883w x16mih1h x972fbf xcfux6l x1qhh985 xm0m39n xt0psk2 xt7dq6l xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x1n5bzlp x173jzuc x1yc6y37 xfs2ol5')]")
            except NoSuchElementException:
                t += 1
            else:
                send_btn.click()
                time.sleep(2)
                break

    def _read_comments(self):
        """ read all saved comments """

        with open(COMMENTS_FILE_PATH, "r") as f:
            comments = json.load(f)
        return comments

    def _write_comments(self, comments):
        """ write all comments """

        with open(COMMENTS_FILE_PATH, "w") as f:
            json.dump(comments, f, indent=4)

    def _get_keywords(self):
        """ Get all tracked keywords in file 'keywords' """

        with open(KEYWORDS_FILE_PATH, "r") as f:
            keywords = f.readlines()

        return [k.strip(" ").strip("\n") for k in keywords]        

    def _eligible_for_dm(self, keywords, comment_text):
        """ Check if a comment contains tracked keywords """

        for k in keywords:
            if k in comment_text:
                return True
        return False

    def get_comments_box_web_element(self, xpath):
        box = None

        t = 0
        while True:

            if t > 2:
                print("Could not find comments.")
                return None

            try:
                box = self.driver.find_element(By.XPATH, xpath)
            except NoSuchElementException:
                time.sleep(2)
                t += 1
            else:
                return box

    def _parse_comments_through_source(self, source) -> list:
    
        soup = BeautifulSoup(source, "html.parser")

        # getting time 
        times = soup.find_all("time")

        user_div_classname = "x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1"

        all_comments = []
        for time in times:
            user_div = time.find_parent(class_=user_div_classname)
            
            date_str = " ".join(time.get_attribute_list("datetime")[0].split(".")[0].split("T"))

            user = user_div.select("span")[0].text.strip()
            comment_text = " ".join(user_div.parent.find_all("span")[-1].text.replace("\n", " ").split())


            all_comments.append({
                "user": user,
                "published_date": date_str,
                "content": comment_text
            })

        return all_comments

    def _is_new_comments(self, source) -> bool:

        if len(self._parse_comments_through_source(source)) > len(self._read_comments()):
            return True
        return False

    def get_comments_source(self, post_id):
        """ Go fetch comments source code on a post page """

        # go to the post
        post_url = BASE_URL + "p/" + post_id
        self.driver.get(post_url)
        time.sleep(5)

        # wait for comments 
        comments_box_source = self.get_comments_box_web_element(xpath=COMMENTS_HTML_ELEMENT_XPATH)
        if not comments_box_source:
            return []
        time.sleep(2)

        t = 0
        preview_scroll_height = 0
        
        # fetching all comments
        while True: 
            # fetch all comments scrolling through the comments's box
            
            script = f"""
                const element = document.getElementsByClassName('{comments_box_source.get_attribute('class')}')[0];
                element.scrollTo(0, element.scrollHeight);
                return element.scrollHeight;
            """

            scroll_height = self.driver.execute_script(script)
            if scroll_height == preview_scroll_height:
                if t >= 2:
                    break

                t += 1
                time.sleep(5)
                continue
            
            t = 0
            preview_scroll_height = scroll_height
            time.sleep(5)

        return self.driver.find_element(By.XPATH, "//div[contains(@class, 'x78zum5 xdt5ytf x1iyjqo2')]").get_attribute("innerHTML")

    def _checking_new_comments(self, post_id) -> list:
        """ Check if someone post a new comment on tracked posts """

        comments_box_source = self.get_comments_source(post_id)

        # is new comments
        if self._is_new_comments(comments_box_source):
            return self._get_new_comments(comments_box_source) # new comments list 
        return []
    
    def _get_new_comments(self, source_code) -> list:
        """ get new comments on a specific post """

        new_comments = []

        comments = self._parse_comments_through_source(source_code)
        saved_comments = self._read_comments()
        for comment in comments:
            if (comment["user"], comment["content"]) in \
                [(c["user"], c["content"]) for c in saved_comments]:
                continue
            else:
                new_comments.append(comment)
        return new_comments
    
    def _get_auto_dm_message_text(self):
        with open(AUTO_DM_MESSAGE_FILE_PATH, "r") as f:
            return f.read()

    def _dm_comments(self, comments):
        """ DM new comments if conform """

        for comment in comments:
            keywords = self._get_keywords()
            if not self._eligible_for_dm(keywords, comment["content"]):
                continue

            message = self._get_auto_dm_message_text()
            print(f"Sending message to '{user}'...")
            self.send_message(user=user, message=message)

                
if __name__ == "__main__":
    
    user = "youssoufmeta"
    InstaBot(driver=driver).go()
