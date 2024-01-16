from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from common_funcs import trunc_addr, init_tel_bot, read_listings, write_listings, maps_to_std

import time
import requests
import traceback

def funda(url, browser, chrome_options, broadcast):
    #Get the telegram bot ready
    params = init_tel_bot()
    if type(params) == 'string':
        return params
    telegram_url, tel_params = params

    #Read all the checked listings into a list so that we can wipe the archive of old listings
    checked_ids = read_listings('funda')
    
    #Open the real estate agency website
    print("Opening Funda")
    browser.get(url)
    #Press accept cookies
    try:
        browser.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]').click()
    except NoSuchElementException:
        pass

    new_listings = 0;
    time.sleep(10)
    listings_arr = []
    #Read all pages
    with open('checked_archive/funda.txt', 'a') as file:
        try:
            while True:
                time.sleep(10)
                listing_part = browser.find_element(By.CLASS_NAME, "pt-4")
                listings = listing_part.find_elements(By.XPATH, '*')#Grab available listings
                print("Number of listings on this page: " + str(len(listings)))
                for listing in listings:
                    #Check if it's an advert
                    try:
                        listing_id = listing.find_element(By.TAG_NAME, 'h2').text
                    except NoSuchElementException:
                        print("Listing is an advert")
                        continue
                    print("*----------------------*")
                    print(listing_id)
                    #Check if it's a huurcomplex
                    try:
                        listing.find_element(By.CLASS_NAME, 'inline.align-middle')
                        print("Huurcomplex... skipping")
                        continue #If this class exist that means it's part of a huurcomplex
                    except NoSuchElementException:
                        pass

                    #Check the price
                    print("Checking price")
                    price_html = listing.find_element(By.TAG_NAME, 'p')
                    price = int(price_html.text.split(' ')[1].replace('.', ''))
                    if price > 1400:
                        print("Too expensive")
                        continue
                    print("Price is fine")

                    #There's no need to check a blacklist since the filter is set to past 24 hours
                    #Check if it's been checked before
                    listing_id = trunc_addr(listing_id)
                    print("Checking archive")
                    listings_arr.append(listing_id + '\n')
                    if listing_id in checked_ids:
                        print("Listing already checked")
                        continue
                    print("New listing")

                    #If good: send notification
                    print("Getting link to listing")
                    hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                    tel_params['text'] = "New suitable rental found: " + hyper_link
                    if broadcast:
                        r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                    file.write(listing_id + '\n')
                    new_listings += 1
                
                #Check if there is more pages
                try:
                    print("Checking for new page")
                    next_page = browser.find_element(By.XPATH, '//*[text()="Volgende"]').find_element(By.XPATH, '..')
                    li = next_page.find_element(By.XPATH, '..')
                    if li.get_attribute('class') == 'disabled':
                        raise InvalidArgumentException
                    print("Going to next page")
                    li.click()
                except (NoSuchElementException, InvalidArgumentException) as e:
                    print("No more pages")
                    break
        except:
            return traceback.format_exc()
    with open('checked_archive/funda.txt', 'w') as file:
        write_listings(file, listings_arr)
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Funda" + ", new listings found: " + str(new_listings))
    return 'Done with Funda' + ", new listings found: " + str(new_listings)
