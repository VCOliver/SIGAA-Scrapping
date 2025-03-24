from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from typing import Final, NoReturn

class SIGAA_Scraper:
    def __init__(self):
       self.driver: Final = webdriver.Firefox()
        
    def login(self, username:str, password: str):
        try:
            self.driver.get("https://autenticacao.unb.br/")
            
            wait = WebDriverWait(self.driver, 15)
            username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='username']")))
            username_input.send_keys("211031842")
            password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
            password_input.send_keys("REDACTED")
            password_input.submit()       
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
    scraper.login("211031842", "REDACTED")
    scraper.wait(5)
    scraper.quit()