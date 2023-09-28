from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

import time
import requests

class Website:
    def __init__(self, url, execution_func):
        self.url = url
        self.exec_func = execution_func

    def execute_search(self, browser, chrome_options):
        report = self.exec_func(self.url, browser, chrome_options)
        return report

    @staticmethod
    def easy(url, browser, chrome_options):
        browser.get(url)
        return 'Unfinished code'

    @staticmethod
    def rotsvast(url, browser, chrome_options):
        #Open a google maps instance
        print("Opening and configuring google maps")
        google_maps = webdriver.Chrome(options = chrome_options)
        google_maps.get('https://www.google.com/maps/')
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

        #Get the telegram bot ready
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
        telegram_url = f'https://api.telegram.org/bot{token}'
        tel_params = {"chat_id": user_id, "text": ""}

        #Open the real estate agency website
        print("Opening Rotsvast")
        browser.get(url)
        try:
            browser.find_element(By.CLASS_NAME, 'mb_cookie_accept_btn').click()
        except ElementNotInteractableException:
            pass

        locations = ['Leiden', 'Amstelveen', 'Amsterdam']
        time.sleep(12)
        browser.find_element(By.CLASS_NAME, 'btn-custom.btn-grey.hidden-lg').click()
        #Select max price as 1500 euros
        browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/button').click()
        browser.find_element(By.XPATH, '//*[@id="search"]/div[5]/div[2]/div[2]/div/div/ul/li[13]/a').click()

        search_box = browser.find_element(By.ID, 'searchPattern')

        

        #Read all the checked listings into a list so that we can wipe the archive of old listings
        print("Reading logged listings")
        checked_ids = []
        with open('checked_archive/rotsvast.txt', 'r') as file:
            for line in file:
                checked_ids.append(line.strip())
        with open('checked_archive/rotsvast.txt', 'w') as file:
            for location in locations:
                #Clear the search box and then type in the next location
                search_box.clear()
                search_box.send_keys(location)
                search_box.send_keys(Keys.RETURN)
                print("Checking " + location)
                blacklist = ["Bezichtiging vol", "Verhuurd"]
                if location == 'Leiden':
                    max_time = 1.17 #1h10min
                else:
                    max_time = 1
                #Loop: check every page
                while True:
                    #Get all listings on the page
                    time.sleep(10)
                    listings = browser.find_elements_by_class_name('residence-gallery.clickable-parent.col-md-4')
                    print("Number of listings on this page: " + str(len(listings)))
                    for listing in listings:
                        listing_address = listing.find_element(By.CLASS_NAME, 'residence-street')
                        print("*----------------------*")
                        print(listing_address.text)

                        #Check if it's available
                        cont = False
                        for phrase in blacklist:
                            try:
                                listing.find_element(By.XPATH, '//div[text()="' + phrase + '"]')
                                cont = True
                                break
                            except NoSuchElementException:
                                pass
                        if cont:
                            continue
                        #Check price
                        print("Checking price")
                        price_html = listing.find_element(By.CLASS_NAME, 'residence-price')
                        price = int(price_html.text.split(' ')[1].replace(',', '').replace('.', ''))/100
                        if price > 15000:
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
                        src_srch.clear()
                        src_srch.send_keys(listing_address.text + ', ' + location)
                        src_srch.send_keys(Keys.RETURN)
                        time.sleep(6)
                        journey_obj = google_maps.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]')#Get the list of ways to get there
                        journeys = journey_obj.find_elements(By.XPATH, '*')#Get all of them
                        journey_lengths = []
                        for i, journey in enumerate(journeys):#Loop through the journeys and save their travel times
                            journey_time = journey.find_element(By.CLASS_NAME, 'Fk3sm.fontHeadlineSmall').text
                            journey_lengths.append(maps_to_std(journey_time))#Convert it to an integer
                        shortest = min(journey_lengths)
                        if shortest > max_time:
                            print("Too far away")
                            continue
                        print("Close enough")

                        #If good: send notification
                        print("Getting link to listing")
                        hyper_link = listing.find_element(By.TAG_NAME, "a").get_attribute('href')
                        tel_params['text'] = "New suitable rental found: " + hyper_link
                        r = requests.post(telegram_url + "/sendMessage", params=tel_params)

                    #Check if there is a next button, not then break
                    try:
                        print("Checking for more pages")
                        next_page = browser.find_element(By.XPATH, '//*[text()="Volgende"]')
                        browser.get(next_page.get_attribute('href'))
                    except NoSuchElementException:
                        print("No more pages")
                        break 
                    except Exception as e:
                        return 'Next page not working correctly: ' + str(e)
            return 'Done with Rotsvast'
            


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
            line = line.split(' ')
            websites[line[0]] = line[1]
    return websites
