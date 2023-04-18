import logging
import os
from typing import Union
import requests
import zipfile

class ChromeDownloader:
    """
    Just use the run() method to download the latest compatible ChromeDriver version for the installed Chrome version
    and extract it to the chrome folder.

    log_level = 0: no logs (default)
    log_level = 1: only errors
    log_level = 2: errors and info
    """
    def __init__(self, log_level = 1):
        self.log_level = log_level
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chrome')
    
    def run(self):
        try:
            if self.chromedriver_path in os.listdir():
                os.rmdir(self.chromedriver_path)
                os.mkdir(self.chromedriver_path)
                if self.log_level >= 2: log("ChromeDriver folder created")

            chrome_version = self._get_chrome_version()
            if self.log_level >= 2: log("Chrome version detected:", chrome_version)

            chromedriver_version = self._get_compatible_chromedriver_version(chrome_version)
            if self.log_level >= 2: log("ChromeDriver version detected:", chromedriver_version)

            self._download_chromedriver(chromedriver_version)
            if self.log_level >= 2: log("ChromeDriver downloaded and extracted to", self.chromedriver_path)

        except Exception as e:
            if self.log_level >= 1: log(f'Error: {e}')
            raise Exception("Error while trying to download ChromeDriver")

    def _get_chrome_version(self):
        try:
            chrome_version = os.popen('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read().strip().split(" ")[-1]
            return chrome_version
        except Exception as e:
            if self.log_level >= 1: log(f'Error: {e}')
            raise Exception("Chrome not installed, please install Chrome and retry")

    def _get_compatible_chromedriver_version(self, chrome_version):
        try:
            chrome_version = '.'.join(chrome_version.split(".")[:3])
            url = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}'
            chromedriver_version = requests.get(url).text.strip()
            return chromedriver_version
        except Exception as e:
            if self.log_level >= 1: log(f'Error: {e}')
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
            if self.log_level >= 1: log(f'Error: {e}')
            raise Exception("Error while trying to download ChromeDriver")


class FileWriter:
    def __init__(self, file_path, auto_overwrite=True, log_level=0):
        self.file_path = file_path
        self.auto_overwrite = auto_overwrite
        self.log_level = log_level

    def write_to_file(self, text:str):
        file_path_exists = os.path.exists(self.file_path)
        if file_path_exists:
            if self.log_level >= 2: log(f"File {self.file_path} already exists.")
            if not self.auto_overwrite:
                confirm = input(f"Do you want to overwrite it? (y/n)")
                if confirm.lower() != 'y':
                    return
            else:
                if self.log_level >= 1: log("Overwriting...")

        backup_file_path = None
        if file_path_exists:
            if self.log_level >= 2: log(f"Creating backup file {self.file_path}.bak...")
            backup_file_path = self.file_path + ".bak"
            os.rename(self.file_path, backup_file_path)
            if self.log_level >= 2: log(f"Backup file created.")

        try:
            if self.log_level >= 2: log(f"Writing file {self.file_path}...")
            with open(self.file_path, 'w', encoding="utf-8") as file:
                file.write(text)
                if self.log_level >= 2: log(f"Written successfully.")
        except Exception as e:
            if self.log_level >= 1: log(f"Error: {e}")
            if backup_file_path:
                os.rename(backup_file_path, self.file_path)
                if self.log_level >= 1: log(f"File restored from backup.")
            else:
                os.remove(self.file_path)
            raise
        finally:
            if backup_file_path:
                os.remove(backup_file_path)
                if self.log_level >= 1: log(f"Backup file removed.")

    def save(self, elements: Union[str, list]):
        output:str
        if isinstance(elements, str):
            output = elements
        elif isinstance(elements, list):
            if len(elements) == 0:
                output = ""
            if isinstance(elements[0], str):
                output = "\n".join(elements)
            else:
                output = "\n".join([str(element) for element in elements])
        
        self.write_to_file(output)


class CookiesCRUD:
    """Cookies CRUD operations
        methods:
            create(key, value)
            read(cookie)
            read_all()
            update(key, value)
            delete(key)
    """
    def __init__(self, driver):
        self.driver = driver
        self.cookies = self.driver.get_cookies()
    
    def read_all(self):
        return self.cookies
    
    def read(self, cookie):
        return self.driver.get_cookie(cookie)

    def create(self, key, value):
        self.driver.add_cookie({'name': key, 'value': value})

    def delete(self, key):
        self.driver.delete_cookie(key)

    def update(self, key, value):
        self.delete(key)
        self.create(key, value)


class LocalStorageCRUD:
    """LocalStorage CRUD operations
        methods:
            create(key, value)
            read(key)
            read_all()
            update(key, value)
            delete(key)
    """
    def __init__(self, driver):
        self.driver = driver
        self.local_storage = self.driver.execute_script("return window.localStorage;")
    
    def read_all(self):
        return self.local_storage

    def read(self, key):
        return self.driver.execute_script(f"return window.localStorage.getItem('{key}');")

    def create(self, key, value):
        self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

    def delete(self, key):
        self.driver.execute_script(f"window.localStorage.removeItem('{key}');")

    def update(self, key, value):
        self.delete_local_storage(key)
        self.add_local_storage(key, value)


logging.basicConfig(filename="logs.log",
                    filemode='a',
                    format='%(asctime)s, %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
def log(*string):
    #logging.log(logging.INFO, string)
    print(" ".join(string))
