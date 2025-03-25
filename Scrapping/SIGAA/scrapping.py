from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from typing import Final, NoReturn

class SIGAA_Scraper:
    def __init__(self):
       self.driver: Final = webdriver.Firefox()
        
    def access_portal(self):
        wait = WebDriverWait(self.driver, 15)
        try:
            self.driver.get("https://sigaa.unb.br/sigaa/public/turmas/listar.jsf")
            
        except Exception as e:
            print(e)
            self.quit()
            self._terminate()
        
    @staticmethod
    def wait(secs) -> None:
        time.sleep(secs)
        
    def quit(self):
        self.driver.quit()
    
    def _terminate(self):
        import sys
        sys.exit(1)

if __name__=="__main__":
    scraper = SIGAA_Scraper()
    scraper.access_portal()
    scraper.wait(5)
    scraper.quit()