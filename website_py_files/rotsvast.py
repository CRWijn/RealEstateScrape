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

def rotsvast(url, browser, chrome_options, broadcast):
    #Get the telegram bot ready
    params = init_tel_bot()
    if type(params) == 'string':
        return params
    telegram_url, tel_params = params

    #Read all the checked listings into a list so that we can wipe the archive of old listings
    checked_ids = read_listings('rotsvast')

    #Open the real estate agency website
    print("Opening Rotsvast")
    browser.get(url)
    try:
        browser.find_element(By.CLASS_NAME, 'mb_cookie_accept_btn').click()
        print("Pressed cookie button")
    except (ElementNotInteractableException, NoSuchElementException):
        pass
    print("Passed cookie button")
    locations = ['Leiden', 'Amstelveen', 'Amsterdam', 'Haarlem']
    time.sleep(12)
    browser.find_element(By.CLASS_NAME, 'btn-custom.btn-grey.hidden-lg').click()
    #Select max price as 1500 euros
    browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/button').click()
    browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/div/ul/li[13]/a').click()
    search_box = browser.find_element(By.ID, 'searchPattern')

    new_listings = 0;
    listings_arr = []
    
    with open('checked_archive/rotsvast.txt', 'a') as file:
        try:#OPEN TRY: ERROR HANDLING
            for location in locations:
                #Clear the search box and then type in the next location
                search_box.clear()
                search_box.send_keys(location)
                search_box.send_keys(Keys.RETURN)
                print("Checking " + location)
                #Loop: check every page
                while True:
                    #Get all listings on the page
                    time.sleep(10)
                    listings = browser.find_elements_by_class_name('residence-gallery.clickable-parent.col-md-4')
                    print("Number of listings on this page: " + str(len(listings)))
                    for listing in listings:
                        listing_address = listing.find_element(By.CLASS_NAME, 'residence-street')
                        city_caps = listing.find_element(By.CLASS_NAME, 'residence-zipcode-place').text.split(' ')[1]
                        city = city_caps[0] + city_caps[1:].lower()
                        if city not in locations:
                            print("Not searching for listing in " + city)
                        print("*----------------------*")
                        print(listing_address.text)
                        
                        #Check price
                        print("Checking price")
                        price_html = listing.find_element(By.CLASS_NAME, 'residence-price')
                        price = int(price_html.text.split(' ')[1].replace(',', '').replace('.', ''))/100
                        if price > 1400:
                            print("Too expensive")
                            continue
                        print("Price is fine")

                        #Check if it's been checked before
                        print("Checking archive")
                        listing_id = listing.get_attribute('id')
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

                    #Check if there is a next button, not then break
                    try:
                        print("Checking for more pages")
                        next_page = browser.find_element(By.XPATH, '//*[text()="Volgende"]')
                        browser.get(next_page.get_attribute('href'))
                    except NoSuchElementException:
                        print("No more pages")
                        break
        except:
            return traceback.format_exc()
    with open('checked_archive/rotsvast.txt', 'w') as file:
        write_listings(file, listings_arr)
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Rotsvast" + ", new listings found: " + str(new_listings))
    return 'Done with Rotsvast' + ", new listings found: " + str(new_listings)
