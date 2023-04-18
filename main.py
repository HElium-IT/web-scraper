from time import sleep
import time
from scraper import WebScraper, WebScraperUser


def run(scraper: WebScraper):
    def get_deals():
        items, driver_elements = scraper.filter_elements(_class="DealCardDynamic-module__card_byn3MbtqkJHcIi783X3tE")
        return items
    
    def get_deal_data_1(deal_div):
         return f"{deal_div['aria-label']}\n"

    def get_deal_data_2(deal_div):
            deal = deal_div.__dict__['contents'][1].__dict__['contents'][0].__dict__['contents'][0]

            percentage = deal.__dict__['contents'][0].__dict__['contents'][0]
            text = deal.__dict__['contents'][1].__dict__['contents'][0]

            return f"\tDeal: {percentage}\t{text}\n"

    def get_deal_data_3(deal_div):
        link = deal_div.__dict__['contents'][0]['href']
        scraper.navigate_to(link)
        prices, driver_elements = scraper.filter_elements(_class="a-offscreen")
        price = prices[0].__dict__['contents'][0]
        return f"\tLink: {link}\n\tPrice: {price}\n"
    

    #get current time
    t = time.time()
    scraper.navigate_to("https://www.amazon.it/deals?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-lightning-deals%2522%252C%2522dealType%2522%253A%2522LIGHTNING_DEAL%2522%252C%2522sorting%2522%253A%2522FEATURED%2522%257D")
    
    items = get_deals()
    scraper.save("raw.html", items)

    items_2 = [f"{get_deal_data_1(item)}{get_deal_data_2(item)}" for item in items]
    scraper.save("data.txt", items_2)

    items_3 = [f"{data}{get_deal_data_3(item)}" for item, data in zip(items, items_2)]
    scraper.save("more_data.txt", items_3)

    log(f"Time elapsed: {time.strftime('%H:%M:%S', time.gmtime(time.time() - t))}")

if __name__ == "__main__":
    user = WebScraperUser(run=run, headless=True, log_level=2)
