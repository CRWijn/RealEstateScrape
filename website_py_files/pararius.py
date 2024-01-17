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

def pararius(url, browser, chrome_options, broadcast):
    #Get the telegram bot ready
    params = init_tel_bot()
    if type(params) == 'string':
        return params
    telegram_url, tel_params = params

    #Read all the checked listings into a list so that we can wipe the archive of old listings
    checked_ids = read_listings('pararius')
    
    #Open the real estate agency website
    print("Opening Pararius")
    browser.get(url)

    time.sleep(5)

    locations = ['Leiden', 'Amstelveen', 'Amsterdam', 'Haarlem']
    
    new_listings = 0;
    listings_arr = []
    #Read all pages
    with open('checked_archive/pararius.txt', 'a') as file:
        try:
            for location in locations:
                #Clear the search box and then type in the next location
                search_box = browser.find_element(By.CLASS_NAME, "autocomplete__input")
                search_box.clear()
                search_box.send_keys(location)
                time.sleep(2)
                search_box.send_keys(Keys.RETURN)
                print("Checking " + location)
                while True:
                    time.sleep(10)
                    listings = browser.find_elements(By.CLASS_NAME, "search-list__item.search-list__item--listing")
                    print("Number of listings on this page: " + str(len(listings)))
                    for listing in listings:
                        #Check the price
                        print("Checking price")
                        price_html = listing.find_element(By.CLASS_NAME, "listing-search-item__price")
                        price = int(price_html.text.split(" ")[1].replace(".", ""))
                        if price > 1400:
                            print("Too expensive")
                            continue
                        print("Price is fine")

                        
                        #Check if it's been checked before
                        listing_id = trunc_addr(listing.find_element(By.CLASS_NAME, "listing-search-item__link.listing-search-item__link--title").text)
                        print("Checking archive")
                        listings_arr.append(listing_id + '\n')
                        if listing_id in checked_ids:
                            print("Listing already checked")
                            continue
                        print("New listing")

                        #If good: send notification
                        print("Getting link to listing")
                        hyper_link = listing.find_element(By.CLASS_NAME, "listing-search-item__link.listing-search-item__link--title").get_attribute('href')
                        tel_params['text'] = "New suitable rental found: " + hyper_link
                        if broadcast:
                            r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                        file.write(listing_id + '\n')
                        new_listings += 1
                    
                    #Check if there is more pages
                    try:
                        print("Checking for new page")
                        next_page = browser.find_element(By.CLASS_NAME, "pagination__link.pagination__link--next")
                        print("Going to next page")
                        browser.get(next_page.get_attribute('href'))
                    except (NoSuchElementException, InvalidArgumentException) as e:
                        print("No more pages")
                        break
        except:
            return traceback.format_exc()
    with open('checked_archive/pararius.txt', 'w') as file:
        write_listings(file, listings_arr)
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Pararius" + ", new listings found: " + str(new_listings))
    return 'Done with Pararius' + ", new listings found: " + str(new_listings)
