from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.keys import Keys
from datetime import datetime

import time
import requests
import traceback

class BadAddress(Exception):
    pass

class Website:
    def __init__(self, url, execution_func):
        self.url = url
        self.exec_func = execution_func

    def execute_search(self, browser, chrome_options):
        report = self.exec_func(self.url, browser, chrome_options)
        return report

    @staticmethod
    def funda(url, browser, chrome_options):
        #Open a google maps instance
        # maps = GoogleMaps(chrome_options)

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
        #Read all pages
        with open('checked_archive/funda.txt', 'w') as file:
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
                        print("Checking archive")
                        file.write(listing_id + '\n')
                        if listing_id in checked_ids:
                            print("Listing already checked")
                            continue
                        print("New listing")

                        #Check google maps for travel time
                        # city = listing.find_element(By.CLASS_NAME, 'text-dark-1.mb-2').text.split(' ')[2]
                        listing_id = trunc_addr(listing_id)
                        # address = listing_id + ', ' + city
                        # max_time = 1.17 if city == 'Leiden' else 1
                        # if maps.search_maps(chrome_options, address, max_time):
                        #     continue

                        #If good: send notification
                        print("Getting link to listing")
                        hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                        tel_params['text'] = "New suitable rental found: " + hyper_link
                        r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                        checked_ids.append(listing_id)
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
                    write_listings(file, checked_ids)#Re-write the checked ids
                    return traceback.format_exc()
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Funda" + ", new listings found: " + str(new_listings))
        return 'Done with Funda' + ", new listings found: " + str(new_listings)

    @staticmethod
    def easy(url, browser, chrome_options):
        #Open a google maps instance
        # maps = GoogleMaps(chrome_options)

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
        locations = ['Leiden', 'Amstelveen', 'Amsterdam', 'Haarlem']

        new_listings = 0;
        
        with open('checked_archive/easy.txt', 'w') as file:
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
                    write_listings(file, checked_ids)
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
                    file.write(listing_id + '\n')
                    if listing_id in checked_ids:
                        print("Listing already checked")
                        continue
                    print("New listing")

                    #Check google maps for travel time
                    # max_time = 1.17 if city == 'Leiden' else 1
                    listing_id = trunc_addr(listing_id)
                    # address = listing_id + ', ' + city
                    # if maps.search_maps(chrome_options, address, max_time):
                    #     continue

                    #If good: send notification
                    print("Getting link to listing")
                    hyper_link = listing.find_element(By.CLASS_NAME, "aanbodEntryLink").get_attribute('href')
                    tel_params['text'] = "New suitable rental found: " + hyper_link
                    r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                    checked_ids.append(listing_id)
                    new_listings += 1
            except:
                    write_listings(file, checked_ids)#Re-write the checked ids
                    return traceback.format_exc()
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Easy Makelaars" + ", new listings found: " + str(new_listings))
        return 'Done with Easy Makelaars' + ", new listings found: " + str(new_listings)

    @staticmethod
    def rotsvast(url, browser, chrome_options):
        #Open a google maps instance
        # maps = GoogleMaps(chrome_options)

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
        except (ElementNotInteractableException, NoSuchElementException):
            pass
        locations = ['Leiden', 'Amstelveen', 'Amsterdam', 'Haarlem']
        time.sleep(12)
        browser.find_element(By.CLASS_NAME, 'btn-custom.btn-grey.hidden-lg').click()
        #Select max price as 1500 euros
        browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/button').click()
        browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/div/ul/li[13]/a').click()
        search_box = browser.find_element(By.ID, 'searchPattern')

        new_listings = 0;
        
        with open('checked_archive/rotsvast.txt', 'w') as file:
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
                            file.write(listing_id + '\n')
                            if listing_id in checked_ids:
                                print("Listing already checked")
                                continue
                            print("New listing")
                            
                            #Check google maps for travel time
                            listing_id = trunc_addr(listing_address.text)
                            # address = listing_id + ', ' + location
                            # if maps.search_maps(chrome_options, address, max_time):
                            #     continue

                            #If good: send notification
                            print("Getting link to listing")
                            hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                            tel_params['text'] = "New suitable rental found: " + hyper_link
                            r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                            checked_ids.append(listing_id)
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
                write_listings(file, checked_ids)#Re-write the checked ids
                return traceback.format_exc()
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Rotsvast" + ", new listings found: " + str(new_listings))
        return 'Done with Rotsvast' + ", new listings found: " + str(new_listings)

    @staticmethod
    def koops(url, browser, chrome_options):
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

        locations = ["Leiden", "Amsterdam", "Amstelveen", "Haarlem"]
        search_box = browser.find_element(By.ID, "free-solo-demo")

        new_listings = 0

        with open('checked_archive/koops.txt', 'w') as file:
            try:
                for location in locations:
                    #This website does not use next buttons for pages
                    try: # Try clearing the search bar
                        browser.find_element(By.CLASS_NAME, "MuiButtonBase-root.MuiIconButton-root.MuiIconButton-sizeMedium.MuiAutocomplete-clearIndicator.css-edpqz1").click()
                    except NoSuchElementException:
                        pass
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
                        price = int(price_html.text.split(' ')[1].replace(',-', '').replace('.', '')) / 100
                        if price > 1400:
                            print("Too expensive")
                            continue
                        print("Price is fine")

                        #Check if it's been checked before
                        print("Checking archive")
                        hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                        listing_id = hyper_link.split("/")[-1].split('.')[0]
                        file.write(listing_id + '\n')
                        if listing_id in checked_ids:
                            print("Listing already checked")
                            continue
                        print("New listing")

                        #Send a link
                        print("Getting link to listing")
                        tel_params['text'] = "New suitable rental found: " + hyper_link
                        r = requests.post(telegram_url + "/sendMessage", params=tel_params)
                        checked_ids.append(listing_id)
                        new_listings += 1
            except:
                write_listings(file, checked_ids)  # Re-write the checked ids
                return traceback.format_exc()
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "- Done with Rotsvast" + ", new listings found: " + str(
            new_listings))
        return 'Done with Koops Makelaardij' + ", new listings found: " + str(new_listings)

class GoogleMaps:
    def __init__(self, chrome_options):
        print("Opening and configuring google maps")
        google_maps = webdriver.Chrome(options = chrome_options)
        google_maps.get('https://www.google.com/maps/')
        time.sleep(4)
        google_maps.find_element(By.CLASS_NAME, 'VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.Nc7WLe').click()#Press directions
        google_maps.find_element(By.ID, 'hArJGc').click()#Press
        time.sleep(4)
        google_maps.find_element(By.XPATH, '//*[@id="omnibox-directions"]/div/div[2]/div/div/div/div[3]/button').click()
        src_srch = google_maps.find_element(By.XPATH, '//*[@id="sb_ifc50"]/input')
        dest_srch = google_maps.find_element(By.XPATH, '//*[@id="sb_ifc51"]/input')
        src_srch.send_keys('Amsterdam Centraal') #Dummy text so that we can set up the time
        dest_srch.send_keys('Amsterdam UMC, locatie AMC, Meibergdreef 9, 1105 AZ Amsterdam')
        dest_srch.send_keys(Keys.RETURN)
        google_maps.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/span/div').click()#Press Leave now for timing
        google_maps.find_element(By.XPATH, '//*[@id=":1"]/div').click()#Press depart at
        time_el = google_maps.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/span[1]/input')
        time_el.clear()
        time_el.send_keys('2:30PM') #Fill in time: 2:30PM
        print("Done configuring maps")
        self.google_maps = google_maps
        self.src_srch = src_srch

    def is_close(self, address, max_time):
        self.src_srch.clear()
        self.src_srch.send_keys(address)
        self.src_srch.send_keys(Keys.RETURN)
        time.sleep(6)
        journey_obj = self.google_maps.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]')#Get the list of ways to get there
        journeys = journey_obj.find_elements(By.XPATH, '*')#Get all of them
        journey_lengths = []
        for i, journey in enumerate(journeys):#Loop through the journeys and save their travel times
            journey_time = journey.find_element(By.CLASS_NAME, 'Fk3sm.fontHeadlineSmall').text
            journey_lengths.append(maps_to_std(journey_time))#Convert it to an integer
        shortest = min(journey_lengths)
        if shortest > max_time:
            print("Too far away")
            return False
        print("Close enough")
        return True

    def search_maps(self, chrome_options, address, max_time):
        skip = False
        for try_count in range(3):# Try accessing the maps a maximum of 3 times
            try:
                print("Attempting to search google maps")
                dist = self.is_close(address, max_time)
                failed = False
                if not dist:
                    skip = True
                skip = False
                break
            except:
                print("Failed to search google maps: " + str(try_count))
                skip = True
                self.google_maps.close()
                self.__init__(chrome_options)
        return skip
        

    def close(self):
        self.google_maps.close()
        

def init_tel_bot():
    try:
        with open('credentials.txt', 'r') as file:
            lines = file.readlines()
            user_id = lines[0].strip()
            token = lines[1].strip()
    except FileNotFoundError:
        print("Can't find file")
        return 'Create a credentials.txt file containing your id'
    except Exception as e:
        print("Reached exception, " + str(e))
        return 'Something wrong with the credentials file' + str(e)
    return (f'https://api.telegram.org/bot{token}', {"chat_id": user_id, "text": ""})

def read_listings(agency_name):
    print("Reading logged listings")
    checked_ids = []
    with open('checked_archive/' + agency_name + '.txt', 'r') as file:
        for line in file:
            checked_ids.append(line.strip())
    return checked_ids

def write_listings(file, listing_ids):
    print("Dumping checked listings")
    for listing_id in listing_ids:
        file.write(listing_id + '\n')
    
    

def maps_to_std(time_string):
    time_lst = time_string.split(' ')
    time_std = 0
    try:
        if 'hr' in time_lst:
            time_std += int(time_lst[0])
        return time_std if len(time_lst) <= 2 else time_std + int(time_lst[-2])/60
    except IndexError:
        print("Invalid time")
        return 999999999
    
        
def read_websites():
    websites = {}
    with open('website_list.txt', 'r') as file:
        for line in file:
            if line[0] == '#':#Basically a comment to skip websites
                continue
            line = line.split(' ')
            websites[line[0]] = line[1]
    return websites

def trunc_addr(address):
    addr_list = address.split(' ')
    for i, addr in enumerate(addr_list):
        try:
            int(addr)
            new_addr = ''
            for j in range(i+1):
                new_addr += addr_list[j] + ' '
            return new_addr[:-1]
        except:
            continue
    return address
