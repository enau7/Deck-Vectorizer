from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

REQUEST_HEADERS = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8',
            'accept-encoding' : 'gzip, deflate',
            'connection' : 'keep-alive',
            'referer' : 'https://www.google.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
}

class Scraper:
    """Introscraper: Gets all data from keys in a single URL"""

    def __init__(self, url, driver: webdriver = None, waiting_class_name = None):
        self.url = url
        self.driver = driver or webdriver.Chrome()
        self.waiting_class_name = None
        self.text = None

    def __exit__(self):
        self.driver.quit()

    def webtext(self):
        self.driver.get(self.url)
        if self.waiting_class_name:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, self.waiting_class_name))
                )
            except Exception as e:
                print(f"WebDriverWait failed... {e}")
        html = self.driver.page_source
        self.text = html
        return html
    
    def close(self):
        self.driver.quit()

    def scrape(self, indexstart, indexend):
        """Returns a list of strings that bound the starting and ending indecies."""
        if not self.text:
            raise RuntimeError("Must call self.webtext() before scrape.")
        text = self.text
        data = []
        index = 0
        while (index != -1):
            index = text.find(indexstart)
            if index == -1:
                break
            text = text[index+len(indexstart):len(text)]
            index = text.find(indexend)
            word = text[0:(index)]
            data.append(word)
        return(data)