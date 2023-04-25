from WebScraper import WebScraper, WebScraperUser
from utils import print_object_infos
import time
import logging

logging.basicConfig(filename='info.log', encoding='utf-8', level=logging.INFO)
Logger = logging.getLogger(__name__)

def run(scraper: WebScraper):
    starting_time = time.time()
    Logger.info(f"Starting time {time.strftime('%H:%M:%S', time.gmtime(starting_time))}")
    scraper.navigate_to("https://www.amazon.com/")
    for element in scraper.get_soup():
        print_object_infos(element)
        break
    pass

if __name__ == "__main__":
    user = WebScraperUser(run=run, headless=True)
