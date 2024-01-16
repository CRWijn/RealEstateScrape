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

import os
import sys
import importlib
import inspect
import time
import requests
import traceback

class BadAddress(Exception):
    pass

class Website:
    def __init__(self, url, execution_func, send_new_listings):
        self.url = url
        self.exec_func = execution_func
        self.broadcast = send_new_listings

    def execute_search(self, browser, chrome_options):
        report = self.exec_func(self.url, browser, chrome_options, self.broadcast)
        return report
        
def read_websites():
    sys.path.append("website_py_files")
    websites = {}
    files = os.listdir("website_py_files")
    for file in files:
        if file == "common_funcs.py" or not ".py" in file:
            continue
        obj = importlib.import_module(file.replace(".py", ''))
        for entry in dir(obj):
            entry_obj = getattr(obj, entry)
            if inspect.isfunction(entry_obj):
                url = get_url(entry)
                if url is not None:
                    websites[entry] = (entry_obj, url)
                else:
                    continue
    return websites

def get_url(name):
    with open('website_list.txt', 'r') as file:
        for line in file:
            if line[0] == '#':#Basically a comment to skip websites
                continue
            line = line.split(' ')
            if line[0] == name:
                return line[1]
    return None

