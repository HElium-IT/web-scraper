from typing import Callable, List
import os
import traceback
import logging
import time

from bs4 import BeautifulSoup
from bs4.element import PageElement

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ChromeDownloader import ChromeDownloader

Logger = logging.getLogger(__name__)

class WebScraperUser:
    """
    WebScraperUser class for using WebScraper class in a more user-friendly way.
    To use it, you need to pass a function to the constructor that will use the WebScraper class.
    The function will be called with the WebScraper class as the first argument.
    """
    def __init__(self, run:Callable, *args, **kwargs):
        starting_time = time.time()
        Logger.info(f"Starting time {time.strftime('%H:%M:%S', time.gmtime(starting_time))}")
        try:
            self.scraper = WebScraper(*args, **kwargs)
            run(self.scraper)
        except (Exception) as e: 
            Logger.error(f"Error: {e} \nTraceback:{traceback.format_exc()}")
        except (KeyboardInterrupt):
            Logger.info('Interrupted')
        finally:
            ending_time = time.time()
            Logger.info(f"Elapsed time: {time.strftime('%H:%M:%S', time.gmtime(ending_time - starting_time))}")
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
    driver: webdriver.Chrome
    soup: BeautifulSoup
    
    
    def __init__(self, chrome_options:Options=default_options, headless:bool=True):
        if headless:
            chrome_options.add_argument("--headless")
            Logger.info('Running in headless mode')

        chromedriver_path = os.path.join(os.path.dirname(__file__), 'chrome', 'chromedriver.exe')
        for i in range(3):
            try:
                self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
                self.driver.maximize_window()
                Logger.info('Chrome driver started')
                #self.localStorageManager = LocalStorageCRUD(driver=self.driver)
                break
            except Exception:
                
                Logger.info("Chromedriver not found, downloading...")
                try:
                    ChromeDownloader().run()
                    Logger.info("Chromedriver downloaded.")
                except Exception as e:
                    Logger.error(f"Error: {e}")
                    Logger.error("Chromedriver download failed, retrying...")

                if i == 2:
                    raise Exception("Chromedriver downloading failed. Download manually and retry.")
    
    def quit(self):
        self.driver.quit()
        Logger.info('Chrome driver stopped')
    
    def navigate_to(self, url:str):
        self.driver.get(url)
        Logger.info(f'Navigated to {url}')
        self.get_soup()
    
    def get_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return self.soup

    def find_driver_element(self, by, value) -> WebElement:
        return self.driver.find_element(filter_by(by), value)
    
    def find_driver_elements(self, by, value) -> List[WebElement]:
        return self.driver.find_elements(filter_by(by), value)

    def find_soup_element(self, tag=None, attrs=None, element=False) -> PageElement:
        if element:
            return element.find(tag, attrs)
        return self.soup.find(tag, attrs)

    def find_soup_elements(self, tag=None, attrs=None, element=False) -> List[PageElement]:
        if element:
            return element.find_all(tag, attrs)
        return self.soup.find_all(tag, attrs)

    def click_driver_element(self, element):
        element.click()
    
    def enter_value_driver_element(self, element, value, enter=True):
        element.clear()
        element.send_keys(value)
        if enter:
            element.send_keys(Keys.ENTER)

def filter_by(by:str):
    if by == "XPATH":
        return By.XPATH
    if by == "CSS_SELECTOR":
        return By.CSS_SELECTOR
    if by == "CLASS_NAME":
        return By.CLASS_NAME
    if by == "ID":
        return By.ID
    if by == "LINK_TEXT":
        return By.LINK_TEXT
    if by == "NAME":
        return By.NAME
    if by == "PARTIAL_LINK_TEXT":
        return By.PARTIAL_LINK_TEXT
    if by == "TAG_NAME":
        return By.TAG_NAME