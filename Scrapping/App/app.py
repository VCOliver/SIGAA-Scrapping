
# Starting app logic
from Telegram.telegram_bot import SIGAAMOS_bot
from Database.database import Database
from SIGAA.scrapping import SIGAA_Scraper
import pandas as pd

class App:
    """
    The App class serves as the main application logic for scraping data from SIGAA,
    storing it in a database, and providing filtered access to the data.
    """
    def __init__(self):
        """
        Initializes the App instance by creating instances of SIGAA_Scraper and Database.
        """
        self.__scraper = SIGAA_Scraper()
        self.__db = Database()
        
    def scrape(self) -> None:
        """
        Scrapes data from the SIGAA portal by accessing the portal and classes,
        and updates the class information.
        """
        self.__scraper.access_portal()
        self.__scraper.access_classes()
        self._data = self.__scraper.update_classes_info(True)
        
    def set_database(self) -> None:
        """
        Stores the scraped data into the database.
        """
        self.__db.create(self._data)
        
    def get_data(self, filter_by='availability') -> pd.DataFrame:
        """
        FOR TESTS!
        Retrieves filtered data from the database.

        Args:
            filter_by (str): The filter criteria for the data. Defaults to 'availability'.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the filtered data.
        """
        self.df = self.__db.filter()
        return self.df
    
    def print_class(self, code: str, /) -> None:
        """
        FOR TESTS!
        Prints the details of a specific class based on its code.

        Args:
            code (str): The unique code of the class to be printed.
        """
        df = self.df[self.df['code'] == code]
        print(df)
        
    def start_bot(self, TOKEN: str) -> None:
        bot = SIGAAMOS_bot(TOKEN, self.__db).use_default_handlers()
        bot.register_handlers()
        self.bot = bot
        
    def run_bot(self) -> None:
        self.bot.run()

    def close(self) -> None:
        self.__scraper.quit()
        self.__db.close()