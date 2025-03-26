from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd

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
        
    def access_classes(self):
        wait = WebDriverWait(self.driver, 10)
        try:
            # Handle the dropdown (wait max 10 seconds)
            dropdown = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="formTurma:inputDepto"]'))
            )
            
            # Check if it's a standard select element
            if dropdown.tag_name.lower() == 'select':
                select = Select(dropdown)
                select.select_by_index(2)  # Second item (index starts at 0)
            else:
                # For custom dropdowns (div/ul/li structure)
                dropdown.click()
                second_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f'{dropdown.XPath}/following-sibling::div/ul/li[3]'))
                )
                second_option.click()

            # Handle the button click
            submit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/form/table/tfoot/tr/td/input[1]'))
            )
            submit_button.click()
            
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Element not found: {str(e)}")
            self._terminate()
    
    def update_classes_info(self, save_in_file=False) -> list[dict]:
        wait = WebDriverWait(self.driver, 20)
        print("Searching on SIGAA...", end='')
        
        try:
            # Find all rows in the table body
            rows = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr"))
            )
        except (NoSuchElementException, TimeoutException) as e:
            print(e)
            self._terminate()

        data = []
        subject_code = subject_name = None

        count = 0
        for row in rows:
            # Get the class attribute to check row type
            row_class = row.get_attribute("class")
            
            if "agrupador" in row_class:
                # This row contains the subject name.
                # Locate the element with class 'tituloDisciplina' and extract its text.
                subject_elem = row.find_element(By.CSS_SELECTOR, ".tituloDisciplina")
                subject_code, subject_name = subject_elem.text.strip().split(' - ')
                
            elif "linhaImpar" in row_class or "linhaPar" in row_class:
                # This row contains the subject details.
                # Find all cells in the row.
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Extract the needed information from each cell.
                numero = cells[0].text.strip()
                ano_periodo = cells[1].text.strip()
                docente = cells[2].text.strip()
                horario = cells[3].text.strip()  # This includes the time info (the tooltip might be hidden in HTML)
                # Optionally, you can extract further details from the 2nd "Horário" cell if needed:
                # horario_extra = cells[4].text.strip()
                vagas_ofertadas = cells[5].text.strip()
                vagas_ocupadas = cells[6].text.strip()
                vagas_disponiveis = int(vagas_ofertadas) - int(vagas_ocupadas)
                local = cells[7].text.strip()
                
                # Append the information as a new record in our data list.
                data.append({
                    "Matéria": subject_name,
                    "Código":subject_code,
                    "N_o": numero,
                    "Ano-Período": ano_periodo,
                    "Docente": docente,
                    "Horário": horario,
                    "Qtde Vagas Ofertadas": vagas_ofertadas,
                    "Qtde Vagas Ocupadas": vagas_ocupadas,
                    "Qtde Vagas Disponíveis": vagas_disponiveis,
                    "Local": local
                })
                count+=1
                if count%10 == 0:
                    print('.', end='')
        print('\nDone!')
        
        if save_in_file:     
            # Create the DataFrame
            df = pd.DataFrame(data)
            file_name = 'classes_info.csv'
            df.to_csv(file_name, index=False)
            print(f"Saved data in {file_name}")
            
        return data
    
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
    scraper.access_classes()
    scraper.update_classes_info()
    scraper.quit()