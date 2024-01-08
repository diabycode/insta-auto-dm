from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--disable-notifications")

# driver initialzation
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()