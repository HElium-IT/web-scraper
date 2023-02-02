class CookiesCRUD:
    def __init__(self, driver):
        self.driver = driver
        self.cookies = self.driver.get_cookies()
    
    def get_all(self):
        return self.cookies
    
    def get(self, cookie):
        return self.driver.get_cookie(cookie)

    def create(self, key, value):
        self.driver.add_cookie({'name': key, 'value': value})

    def delete(self, key):
        self.driver.delete_cookie(key)

    def update(self, key, value):
        self.delete(key)
        self.create(key, value)

class LocalStorageCRUD:
    def __init__(self, driver):
        self.driver = driver
        self.local_storage = self.driver.execute_script("return window.localStorage;")
    
    def get_all(self):
        return self.local_storage

    def get(self, key):
        return self.driver.execute_script(f"return window.localStorage.getItem('{key}');")

    def create(self, key, value):
        self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

    def delete(self, key):
        self.driver.execute_script(f"window.localStorage.removeItem('{key}');")

    def update(self, key, value):
        self.delete_local_storage(key)
        self.add_local_storage(key, value)