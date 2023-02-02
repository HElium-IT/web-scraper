import os
import Levenshtein
import traceback
from typing import Callable
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from downloader import ChromeDownloader
from utils import CookiesCRUD#, LocalStorageCRUD


class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
    pass

class WebScraperUser:
    def __init__(self, run:Callable, *args, **kwargs):
        try:
            self.scraper = WebScraper(*args, **kwargs)
            run(self.scraper)
            pass
        except (Exception) as e:
            traceback.print_exception(type(e), e, e.__traceback__)
        except (KeyboardInterrupt):
            print('Interrupted')
        finally:
            self.scraper.quit()

class WebScraper:
    default_options = Options()
    default_options.add_argument("--disable-extensions")
    default_options.add_argument("--disable-gpu")
    default_options.add_argument("--no-sandbox")
    default_options.add_argument("--disable-dev-shm-usage")
    
    
    def __init__(self, chrome_options:Options=default_options, headless:bool=True):
        if headless:
            chrome_options.add_argument("--headless")
        self.chrome_options = chrome_options


        chromedriver_path = os.path.join(os.path.dirname(__file__), 'chrome', 'chromedriver.exe')
        for i in range(3):
            try:
                self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
                self.driver.maximize_window()
                print('Chrome driver started')
                self.cookieManager = CookiesCRUD(driver=self.driver) 
                #self.localStorageManager = LocalStorageCRUD(driver=self.driver)
                break
            except SessionNotCreatedException:
                
                print("Chrome not found, downloading...")
                ChromeDownloader()
                print("Chrome downloaded, retrying...")
                if i == 2:
                    raise Exception("Chrome not found, download manually and retry")

    def quit(self):
        print('Closing Chrome driver')
        self.driver.quit()

    def navigate_to(self, url):
        print(f'Navigating to {url}')
        self.driver.get(url)
        self.driver_elements = self.driver.find_elements_by_xpath('//*')
        self.soup_elements = BeautifulSoup(self.driver.page_source, 'html.parser').find_all()
        
    def enter_value(self, element, value, enter=True):
        try:
            element.clear()
            element
            element.send_keys(value)
            if enter:
                element.send_keys(Keys.ENTER)
        except NoSuchElementException:
            raise NotFoundError("Input not found")

    def click_button(self, element):
        try:
            element.click()
        except NoSuchElementException:
            raise NotFoundError("Button not found") 

    def get_webelements(self, bs_elements):
        found_selectors = set()
        webelements = []
        for element in bs_elements:
            selector = element.name
            if 'class' in element.attrs:
                if isinstance(element.attrs['class'], list):
                    for _class in element.attrs['class']:
                        selector += '.' + _class
                else:
                    selector += '.' + element.attrs['class']
            if 'id' in element.attrs:
                selector += '#' + element.attrs['id']
            
            if selector in found_selectors:
                continue
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            found_selectors.add(selector)
            webelements.extend(elements)
        return webelements

    def filter_elements(self, **kwargs):
        filtered_elements = self.soup_elements
        for key, value in kwargs.items():
            if key in ["_class", "class"]:
                key = "class"
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and value in elem[key]]
            else:
                key = key.replace("_", "-")
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and elem[key] == value]
        print(f"found {len(filtered_elements)} elements with {kwargs}")
        #print(filtered_elements)
        return filtered_elements, self.get_webelements(filtered_elements)

    def filter_similar_elements(self, threshold:float=0.2, **kwargs):
        filtered_elements = self.soup_elements
        for key, value in kwargs.items():
            if key in ["class_", "class"]:
                key = "class"
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and any(Levenshtein.distance(value,x)/len(x) <= threshold for x in elem[key].split())]
            else:
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and Levenshtein.distance(value, elem[key])/len(elem[key]) <= threshold]
        
        print(f"found {len(filtered_elements)} similar elements with {kwargs}")
        #print(filtered_elements)
        return filtered_elements, self.get_webelements(filtered_elements)