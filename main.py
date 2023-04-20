import time
from scraper import WebScraper, WebScraperUser
from utils import log

def run(scraper: WebScraper):
    def navigate_to_page(x):
        deals_link = "https://www.amazon.it/deals?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-lightning-deals%2522%252C%2522dealType%2522%253A%2522LIGHTNING_DEAL%2522%252C%2522sorting%2522%253A%2522BY_DISCOUNT_ASCENDING%2522%257D"
        scraper.navigate_to(deals_link)

        for _ in range(x):
            _, elements = scraper.filter_elements(_class="a-last", get_web_elements=True)
            scraper.click_button(elements[0])
            time.sleep(1)
        scraper.reset_soup()


    def get_deals_divs():
        items, _ = scraper.filter_elements(
            _class="DealCardDynamic-module__card_byn3MbtqkJHcIi783X3tE")
        return items

    def get_deal_data(div):
        label = div.get('aria-label', "NaN")

        scraper.filter_elements(keep_soup=True, data_deal_id=div.attrs['data-deal-id'])
        
        soup, _ = scraper.filter_elements(_class="DealLink-module__dealLink_3v4tPYOP4qJj9bdiy0xAT")
        try:
            link = soup[0].attrs['href']
        except:
            link = "NaN"

        soup, _ = scraper.filter_elements(_class="BadgeAutomatedLabel-module__badgeAutomatedLabel_2Teem9LTaUlj6gBh5R45wd")
        try:
            percentage = soup[0].text
        except:
            percentage = "NaN"

        soup, _ = scraper.filter_elements(_class="DealMessaging-module__dealMessaging_1EIwT6BUaB6vCKvPVEbAEV")
        try:
            text = soup[0].text
        except:
            text = "NaN"

        scraper.reset_soup()
        return {
            "label":label,
            "percentage":percentage,
            "text":text,
            "link": link
            }

    def get_deal_data_2(link):
        scraper.navigate_to(link)

        soup, _ = scraper.filter_elements(id="acrCustomerReviewText", _class="a-size-base")
        try:
            rating = soup[0].text
        except:
            rating = "NaN"

        soup, _ = scraper.filter_elements(_class="reinventPricePriceToPayMargin")
        try:
            price = soup[0].snap.text
        except:
            price = "NaN"

        return {
            "rating":rating,
            "price":price
            }

    t = time.time()

    for i in range(100_000):
        log(f"ITERATION {i+1} |{'-'*100}")

        try:
            navigate_to_page(i)
        except:
            break

        if i == 0:
            # Accept cookies
            _, elements = scraper.filter_elements(id="sp-cc-rejectall-link", get_web_elements=True)
            scraper.click_button(elements[0])

        t_i = time.time()
        divs = get_deals_divs()
        # scraper.save(f"divs{i}.txt", [str(div) for div in divs])

        items = [get_deal_data(div) for div in divs]
        # scraper.save(f"items{i}.txt", items)

        enhanced_items = [item | get_deal_data_2(item['link']) for item in items]
        scraper.save(f"enhanced_items{i}.txt", enhanced_items)

        log(f"\tDelta Time elapsed: {time.strftime('%H:%M:%S', time.gmtime(time.time() - t_i))}\
            \tTotal time elapsed: {time.strftime('%H:%M:%S', time.gmtime(time.time() - t))}")
        

if __name__ == "__main__":
    user = WebScraperUser(run=run, headless=True, log_level=2)
