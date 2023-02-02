import os
import Levenshtein
import traceback
from typing import Callable, Union
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from utils import ChromeDownloader, FileWriter, CookiesCRUD#, LocalStorageCRUD

class WebScraperUser:
    """
    WebScraperUser class for using WebScraper class in a more user-friendly way.
    To use it, you need to pass a function to the constructor that will use the WebScraper class.
    The function will be called with the WebScraper class as the first argument.
    
    Example:
        def run(scraper):
            scraper.get('https://www.google.com')
            scraper.find_element('input').send_keys('Hello World')
            scraper.find_element('input').send_keys(Keys.ENTER)
            print(scraper.find_element('h3').text)
        WebScraperUser(run)
    
    """
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
    """
    WebScraper class for scraping websites using Selenium and BeautifulSoup libraries.
    The class is meant to be used as a base class for other classes that will implement the scraping logic.
    The class provides methods for navigating to a website, entering values in inputs, clicking buttons, etc.
    If chromedriver is not found, it will be downloaded automatically.
    Default options for Chrome are:
        --disable-extensions
        --disable-gpu
        --no-sandbox
        --disable-dev-shm-usage
    If headless is True, the following option is added:
        --headless
    If you want to add more options, you can pass a selenium.webdriver.chrome.options.Options object to the constructor.
    
    log_level = 0: no logs (default)
    log_level = 1: only errors 
    log_level = 2: errors and info
    """
    default_options = Options()
    default_options.add_argument("--disable-extensions")
    default_options.add_argument("--disable-gpu")
    default_options.add_argument("--no-sandbox")
    default_options.add_argument("--disable-dev-shm-usage")
    
    
    def __init__(self, chrome_options:Options=default_options, headless:bool=True, log_level:int=0):
        self.writer = None
        self.log_level = log_level
        if headless:
            chrome_options.add_argument("--headless")
            if self.log_level >= 2: print('Running in headless mode')

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
                
                if self.log_level >= 1: print("Chromedriver not found, downloading...")
                try:
                    ChromeDownloader(log_level=log_level).run()
                    if self.log_level >= 1: print("Chromedriver downloaded, retrying...")
                except Exception as e:
                    if self.log_level >= 1: print(f"Error: {e}")
                    if self.log_level >= 1: print("Chromedriver download failed, retrying...")

                if i == 2:
                    raise Exception("Chromedriver downloading failed. Download manually and retry.")

    def quit(self):
        if self.log_level >= 2: print('Closing Chrome driver')
        self.driver.quit()

    def navigate_to(self, url):
        if self.log_level >= 2: print(f'Navigating to {url}')
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

    def get_web_elements(self, bs_elements):
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

    def filter_elements(self, get_web_elements=False, **kwargs):
        filtered_elements = self.soup_elements
        for key, value in kwargs.items():
            if key in ["_class", "class"]:
                key = "class"
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and value in elem[key]]
            else:
                key = key.replace("_", "-")
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and elem[key] == value]
        if self.log_level >= 2: print(f"found {len(filtered_elements)} elements with {kwargs}")
        #print(filtered_elements)
        if get_web_elements:
            return filtered_elements, self.get_web_elements(filtered_elements)
        return filtered_elements

    def filter_similar_elements(self, get_web_elements=False, threshold:float=0.2, **kwargs):
        filtered_elements = self.soup_elements
        for key, value in kwargs.items():
            if key in ["class_", "class"]:
                key = "class"
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and any(Levenshtein.distance(value,x)/len(x) <= threshold for x in elem[key].split())]
            else:
                filtered_elements = [elem for elem in filtered_elements if elem.has_attr(key) and Levenshtein.distance(value, elem[key])/len(elem[key]) <= threshold]
        
        if self.log_level >= 2: print(f"found {len(filtered_elements)} similar elements with {kwargs}")
        #print(filtered_elements)
        if get_web_elements:
            return filtered_elements, self.get_web_elements(filtered_elements)
        return filtered_elements
    
    def save(self, file_name:str=None, elements:Union[str, list]=None):
        scraped_dir = os.path.join(os.getcwd(), 'scraped')
        if not os.path.exists(scraped_dir):
            os.mkdir(scraped_dir)
        file_path = os.path.join(scraped_dir, file_name)

        try:
            FileWriter(file_path=file_path, log_level=self.log_level).save(elements)
        except Exception as e:
            if self.log_level >= 1: print(f"Error: {e}")
            if self.log_level >= 1: print("Saving failed")


class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
    pass