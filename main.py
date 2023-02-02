from time import sleep
from scraper import WebScraper, WebScraperUser


def run(scraper: WebScraper):
    scraper.navigate_to('https://www.youtube.com/')
    sleep(3)
    
    soup_elements, driver_elements = scraper.filter_elements(_class='yt-spec-button-shape-next--filled')
    scraper.click_button(driver_elements[1])
    sleep(3)
    
    soup_, driver_ = scraper.filter_elements(placeholder="Cerca")
    scraper.enter_value(driver_[0], "python")
    sleep(3)

    soup_, driver_ = scraper.filter_elements(id="video-title")
    videos_meta = soup_

    soup_, driver_ = scraper.filter_elements(id="channel-name")
    videos_channel_name = soup_

    videos_data = [f"%VIDEO = {video}\n%CANALE= {channel}" for video, channel in zip(videos_meta, videos_channel_name)]
    scraper.save(videos_data)

if __name__ == "__main__":
    user = WebScraperUser(run=run, headless=False)
