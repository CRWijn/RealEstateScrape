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
import time

from website import Website
from website import read_websites

if __name__ == '__main__':
    #Setup all the selenium stuff
    chrome_options = Options()
    chrome_options.headless = True
    chrome_service = ChromeService('chromedriver')
    chrome_service.creationflags = CREATE_NO_WINDOW
    browser = webdriver.Chrome(options = chrome_options, service = chrome_service)

    #Read out all the supported websites
    website_dict = read_websites()
    websites = []
    for site in website_dict:
        new_site = Website(website_dict[site], getattr(Website, site))
        websites.append(new_site)

    #Setup periodicity
    WAIT_THRESHOLD = 300 # 5-minutes

    #Loop through websites and execute the code for them
    while True:
        start_wait = time.time()
        #LOG: Start time
        for site in websites:
            site.execute_search()
        execution_time = time.time()-start_wait
        #Log: Execution time and iteration results
        
        #Only perform the search every WAIT_THRESHOLD seconds
        if execution_time < WAIT_THRESHOLD:
            time.sleep(WAIT_THRESHOLD-exeuction_time)
        
