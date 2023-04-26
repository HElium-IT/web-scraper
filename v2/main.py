from WebScraper import WebScraper, WebScraperUser
import time
import logging
import json

logging.basicConfig(filename='info.log', encoding='utf-8', level=logging.INFO)
Logger = logging.getLogger(__name__)

def run(scraper: WebScraper):
    items = dict()
    def navigate_to_page(x):
        Logger.info(f"Navigating to deals page {x}")
        deals_link = "https://www.amazon.it/deals?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-lightning-deals%2522%252C%2522dealType%2522%253A%2522LIGHTNING_DEAL%2522%252C%2522sorting%2522%253A%2522BY_DISCOUNT_ASCENDING%2522%257D"
        scraper.navigate_to(deals_link)

        if x == 0:
            Logger.info("Rejecting cookies")
            button = scraper.find_driver_element("ID", "sp-cc-rejectall-link")
            scraper.click_driver_element(button)

        for _ in range(x):
            link_element = scraper.find_driver_element("PARTIAL_LINK_TEXT", 'Avanti')
            scraper.click_driver_element(link_element)
            time.sleep(1)
        
        scraper.get_soup()
    
    def get_text(element):
        try:
            return element.text
        except:
            return "NaN"
    
    def get_attr(element, key):
        try:
            return element.attrs[key]
        except:
            return "NaN"
    
    def gather_page_informations(x):
        navigate_to_page(x)
        deals_divs = scraper.find_soup_elements("div", {'class':"DealCardDynamic-module__card_byn3MbtqkJHcIi783X3tE"})
        Logger.info(f"Found {len(deals_divs)} deals divs")

        Logger.info("Gathering basic informations")
        to_gather = []
        for div in deals_divs:
            label = get_attr(div, 'aria-label')
            if label == "Nan":
                continue

            label = label [9:]    
            if label in items:
                continue
            
            item = {
                'label':label
            }
            items[label] = item
            try:
                item['link'] = get_attr(scraper.find_soup_element('a', {'class':"DealCardDynamic-module__linkOutlineOffset_2XU8RDGmNg2HG1E-ESseNq"}, div), 'href')
                item['deal_label_1'] = get_text(scraper.find_soup_element(None, {'class':"BadgeAutomatedLabel-module__badgeAutomatedLabel_2Teem9LTaUlj6gBh5R45wd"}, div))
                item['deal_label_2'] = get_text(scraper.find_soup_element(None, {'class': "DealMessaging-module__dealMessaging_1EIwT6BUaB6vCKvPVEbAEV"}, div))
            except Exception as e:
                Logger.error(f"Error while gathering basic informations [{label}]: {e}")
                item['error'] = True
            finally:
                to_gather.append(label)

        Logger.info("Gathering advanced informations")
        for label in to_gather:
            item = items[label]

            try:
                Logger.info(f"Navigating to {label}")
                # Navigate to deal link
                scraper.navigate_to(item['link'])
                item['price'] = get_text(scraper.find_soup_element('span', {'class':"a-offscreen"}))

                coupon_badge = scraper.find_soup_element('i', {'class':"newCouponBadge"})
                if coupon_badge is not None:
                    item['coupon'] = True #get_text(scraper.find_soup_element('label', None, coupon_badge))

            except Exception as e:
                Logger.error(f"Error while gathering advanced informations [{label}]: {e}")
                item['error'] = True
            finally:

                with open(f"scraped/data_{x}.txt", "a") as f:
                    print(json.dumps(item, indent= 2), file=f)
    
    starting_time = time.time()
    Logger.info(f"Starting time {time.strftime('%H:%M:%S', time.gmtime(starting_time))}")

    for x in range(100):
        gather_page_informations(x)

    ending_time = time.time()
    Logger.info(f"Elapsed time: {time.strftime('%H:%M:%S', time.gmtime(ending_time - starting_time))}")
    while True:
        pass

if __name__ == "__main__":
    user = WebScraperUser(run=run, headless=True)
