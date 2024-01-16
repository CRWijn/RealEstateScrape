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

def easy(url, browser, chrome_options, broadcast):
    #Get the telegram bot ready
    params = init_tel_bot()
    if type(params) == 'string':
        return params
    telegram_url, tel_params = params

    #Read all the checked listings into a list so that we can wipe the archive of old listings
    checked_ids = read_listings('easy')
    
    #Open the real estate agency website
    print("Opening Easy Makelaars")
    browser.get(url)
    locations = ['Leiden', 'Amstelveen', 'Amsterdam', 'Haarlem', 'Hilversum']

    new_listings = 0;
    listings_arr = []

    with open('checked_archive/easy.txt', 'a') as file:
        try:
            for tries in range(3):
                try: #Sometimes the middle can't be found so just try refreshing twice, otherwise throw an error
                    time.sleep(10)
                    housing_section = browser.find_elements(By.CLASS_NAME, 'middle')
                    if len(housing_section) == 3:
                        listings = housing_section[2].find_element(By.TAG_NAME, 'ul').find_elements(By.XPATH, '*')
                    else:# Bug where [2] was giving index error, my assumption is that one of the "middle" classes hadn't loaded yet so it was only 2 long
                        listings = housing_section[1].find_element(By.TAG_NAME, 'ul').find_elements(By.XPATH, '*')
                    succeeded = True
                    break
                except:#Try refreshing the page
                    listings = browser.find_elements(By.CLASS_NAME, 'middle')[1].find_element(By.TAG_NAME, 'ul').find_elements(By.XPATH, '*')
                    succeeded = False
                    browser.refresh()
            if not succeeded: #Something beyond went wrong
                return traceback.format_exc()
            print("Number of listings on this page: " + str(len(listings)))
            for listing in listings:
                listing_id = listing.find_element(By.CLASS_NAME, 'street-address').text
                print("*----------------------*")
                print(listing_id)
                
                #Check if it's in one of the locations
                city = listing.find_element(By.CLASS_NAME, 'locality').text
                if not city in locations:
                    print("Not looking for listings in city: " + city)
                    continue

                #Check price
                print("Checking price")
                price_html = listing.find_element(By.CLASS_NAME, 'kenmerkValue')
                price = int(price_html.text.split(' ')[1].split(',')[0].replace('.', ''))
                if price > 1400:
                    print("Too expensive")
                    continue
                print("Price is fine")

                #Check if it's been checked before
                print("Checking archive")
                listings_arr.append(listing_id + '\n')
                if listing_id in checked_ids:
                    print("Listing already checked")
                    continue
                print("New listing")

                #If good: send notification
                print("Getting link to listing")
                hyper_link = listing.find_element(By.CLASS_NAME, "aanbodEntryLink").get_attribute('href')
                tel_params['text'] = "New suitable rental found: " + hyper_link
                if broadcast:
                    r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                file.write(listing_id + '\n')
                new_listings += 1
        except:
                return traceback.format_exc()
    with open('checked_archive/easy.txt', 'w') as file:
        write_listings(file, listings_arr)
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Easy Makelaars" + ", new listings found: " + str(new_listings))
    return 'Done with Easy Makelaars' + ", new listings found: " + str(new_listings)
