import os
import requests
import zipfile

class ChromeDownloader:
    def __init__(self):
        # Create a folder to store the ChromeDriver
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chrome')
        if self.chromedriver_path not in os.listdir():
            os.mkdir(self.chromedriver_path)

        chrome_version = self._get_chrome_version()
        print("Chrome version detected:", chrome_version)

        chromedriver_version = self._get_compatible_chromedriver_version(chrome_version)
        print("ChromeDriver version detected:", chromedriver_version)

        self._download_chromedriver(chromedriver_version)
        print("ChromeDriver downloaded and extracted to", self.chromedriver_path)

    def _get_chrome_version(self):
        try:
            chrome_version = os.popen('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read().strip().split(" ")[-1]
            return chrome_version
        except Exception as e:
            print(f'Error: {e}')
            raise Exception("Chrome not installed, please install Chrome and retry")

    def _get_compatible_chromedriver_version(self, chrome_version):
        try:
            chrome_version = '.'.join(chrome_version.split(".")[:3])
            url = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}'
            chromedriver_version = requests.get(url).text.strip()
            return chromedriver_version
        except Exception as e:
            print(f'Error: {e}')
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
            print(f'Error: {e}')
            raise Exception("Error while trying to download ChromeDriver")