import logging
import os
import requests
import zipfile

Logger = logging.getLogger(__name__)

class ChromeDownloader:
    """
    Just use the run() method to download the latest compatible ChromeDriver version for the installed Chrome version
    and extract it to the chrome folder.
    """
    def __init__(self):
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chrome')
    
    def run(self):
        try:
            if self.chromedriver_path in os.listdir():
                os.rmdir(self.chromedriver_path)
            if self.chromedriver_path not in os.listdir():
                os.mkdir(self.chromedriver_path)
                Logger.info("ChromeDriver folder created")

            chrome_version = self._get_chrome_version()
            Logger.info(f"Chrome version detected: {chrome_version}")

            chromedriver_version = self._get_compatible_chromedriver_version(chrome_version)
            Logger.info(f"ChromeDriver version detected: {chromedriver_version}")

            self._download_chromedriver(chromedriver_version)
            Logger.info(f"ChromeDriver downloaded and extracted to {self.chromedriver_path}")

        except Exception as e:
            Logger.error(f'Error: {e}')
            raise Exception("Error while trying to download ChromeDriver")

    def _get_chrome_version(self):
        try:
            chrome_version = os.popen('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read().strip().split(" ")[-1]
            return chrome_version
        except Exception as e:
            Logger.error(f'Error: {e}')
            raise Exception("Chrome not installed, please install Chrome and retry")

    def _get_compatible_chromedriver_version(self, chrome_version):
        try:
            chrome_version = '.'.join(chrome_version.split(".")[:3])
            url = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}'
            chromedriver_version = requests.get(url).text.strip()
            return chromedriver_version
        except Exception as e:
            Logger.error(f'Error: {e}')
            raise Exception("Error while trying to fetch compatible ChromeDriver version")

    def _download_chromedriver(self, chromedriver_version):
        try:
            url = f'https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_win32.zip'
            chromedriver_zip = os.path.join(self.chromedriver_path, 'chromedriver.zip')
            with open(chromedriver_zip, "wb") as f:
                response = requests.get(url)
                f.write(response.content)
            with zipfile.ZipFile(chromedriver_zip, 'r') as zip_ref:
                zip_ref.extractall(self.chromedriver_path)
            os.remove(chromedriver_zip)
        except Exception as e:
            Logger.error(f'Error: {e}')
            raise Exception("Error while trying to download ChromeDriver")

