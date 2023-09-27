from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW
from fake_useragent import UserAgent
import time

from website import Website
from website import read_websites
from logger import CustomLogger

if __name__ == '__main__':
    #Setup all the selenium stuff
    chrome_options = Options()
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'--user-agent={user_agent}')
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_service = ChromeService('chromedriver')
    #These two stop a window from being created, if u dont want it uncomment them
    chrome_options.headless = True
    chrome_service.creationflags = CREATE_NO_WINDOW
    #----------------------------------------------
    browser = webdriver.Chrome(options = chrome_options, service = chrome_service)

    #Read out all the supported websites
    website_dict = read_websites()
    websites = []
    for site in website_dict:
        new_site = Website(website_dict[site], getattr(Website, site))
        websites.append(new_site)

    #Setup periodicity
    WAIT_THRESHOLD = 300 # 5-minutes
    logger = CustomLogger()

    #Loop through websites and execute the code for them
    while True:
        start_wait = time.time()
        #LOG: Start time
        for site in websites:
            try:
                report = site.execute_search(browser, chrome_options)
                logger.log(report)
            except Exception as e:
                logger.log("Error in main: " + str(e))
        execution_time = time.time()-start_wait
        #LOG: Execution time and iteration results
        logger.log('Full execution took: ' + str(execution_time) + 's')
        
        #Only perform the search every WAIT_THRESHOLD seconds
        if execution_time < WAIT_THRESHOLD:
            time.sleep(WAIT_THRESHOLD-exeuction_time)
        
