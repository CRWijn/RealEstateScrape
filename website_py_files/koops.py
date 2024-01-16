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

def koops(url, browser, chrome_options, broadcast):
    # Get the telegram bot ready
    params = init_tel_bot()
    if type(params) == 'string':
        return params
    telegram_url, tel_params = params

    # Read all the checked listings into a list so that we can wipe the archive of old listings
    checked_ids = read_listings('koops')

    # Open the real estate agency website
    print("Opening Koops Makelaardij")
    browser.get(url)
    time.sleep(5)

    #Select price range and rent
    price_select = Select(browser.find_element(By.NAME, "price_range"))
    price_select.select_by_value("0;1500")
    rent_select = Select(browser.find_element(By.NAME, "rent_or_sale"))
    rent_select.select_by_value("rent")

    locations = ["Leiden", "Amsterdam", "Amstelveen", "Haarlem", 'Hilversum']

    new_listings = 0
    listings_arr = []

    with open('checked_archive/koops.txt', 'a') as file:
        try:
            for location in locations:
                #This website does not use next buttons for pages
                try: # Try clearing the search bar
                    clear_button = browser.find_element(By.CLASS_NAME, "MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeMedium.MuiAutocomplete-clearIndicator.css-edpqz1")
                    a = ActionChains(browser)
                    a.move_to_element(clear_button).click().perform()
                except NoSuchElementException:
                    pass
                try:
                    search_box = browser.find_element(By.CLASS_NAME, "MuiOutlinedInput-input.MuiInputBase-input.MuiInputBase-inputAdornedEnd.MuiAutocomplete-input.MuiAutocomplete-inputFocused.css-1uvydh2")
                except NoSuchElementException:
                    search_box = browser.find_element(By.ID, "free-solo-demo")
                search_box.send_keys(location)
                search_box.send_keys(Keys.RETURN)
                print("Checking " + location)
                time.sleep(10)
                listings = browser.find_elements(By.CLASS_NAME, "c-gallery-item.js-gallery-item.horizontal")
                print("Number of listings in " + location + ": " + str(len(listings)))
                for listing in listings:
                    listing_address = listing.find_element(By.CLASS_NAME, "street").text
                    print("*----------------------*")
                    print(listing_address)

                    #Check Price
                    print("Checking price")
                    price_html = listing.find_element(By.CLASS_NAME, 'price')
                    price = int(price_html.text.split(' ')[1].replace(',-', '').replace('.', ''))
                    if price > 1400:
                        print("Too expensive")
                        continue
                    print("Price is fine")

                    #Check if it's been checked before
                    print("Checking archive")
                    hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                    listing_id = hyper_link.split("/")[-1].split('.')[0]
                    listings_arr.append(listing_id + '\n')
                    if listing_id in checked_ids:
                        print("Listing already checked")
                        continue
                    print("New listing")

                    #Send a link
                    print("Getting link to listing")
                    tel_params['text'] = "New suitable rental found: " + hyper_link
                    if broadcast:
                        r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                    file.write(listing_id + '\n')
                    new_listings += 1
        except:
            return traceback.format_exc()

    with open('checked_archive/koops.txt', 'w') as file:
        write_listings(file, listings_arr)
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Koops Makelaardij" + ", new listings found: " + str(
        new_listings))
    return 'Done with Koops Makelaardij' + ", new listings found: " + str(new_listings)
