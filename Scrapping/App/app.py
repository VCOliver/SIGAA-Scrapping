# Starting app logic
from Telegram.telegram_bot import SIGAAMOS_bot
from Database.database import Database
from SIGAA.scrapping import SIGAA_Scraper
import pandas as pd

import threading
import time
from datetime import datetime
import asyncio  # Added for event loop management

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
        self._stop_event = threading.Event()  # Event to signal threads to stop
        
    def setup(self, TOKEN: str):
        self.scrape()
        self.set_database()
        self.start_bot(TOKEN)
        
    def run(self):
        """
        Starts the scraper in a separate thread and runs the bot in the main thread.
        """
        self.scraper_thread = threading.Thread(target=self.run_scraper, daemon=False)
        self.scraper_thread.start()
        self.run_bot()  # Run the bot in the main thread
        
    def scrape(self) -> None:
        """
        Scrapes data from the SIGAA portal by accessing the portal and classes,
        and updates the class information.
        """
        self.__scraper.access_portal()
        self.__scraper.access_classes()
        self._data = self.__scraper.update_classes_info(True)
        
    def run_scraper(self):
        """
        Runs the scraper in a loop until the stop event is set.
        """
        # Create and set an event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while not self._stop_event.is_set():  # Loop until stop event is set
            try:
                self.scrape()
                self.__db.update_classes(self._data)
                print(f"Database updated at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                loop.run_until_complete(self.bot._notify_users())  # Run the coroutine in the thread's event loop
            except Exception as e:
                print(f"Scraper encountered an error: {e}")
                # Restart WebDriver if necessary
                self.__scraper.quit()
                self.__scraper = SIGAA_Scraper()
            finally:
                for _ in range(2 * 60):  # Sleep for 10 minutes in 1-second intervals
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)

        # Close the event loop when the thread stops
        loop.close()
        
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
        """
        Runs the bot in the main thread.
        """
        try:
            asyncio.run(self.bot.run())  # Use asyncio.run to execute the bot's coroutine
        except Exception as e:
            print(f"Bot encountered an error: {e}")

    def close(self) -> None:
        """
        Signals threads to stop and waits for them to finish.
        """
        self._stop_event.set()  # Signal threads to stop
        self.scraper_thread.join(timeout=5)  # Wait for scraper thread to finish with timeout
        self.__scraper.quit()
        self.__db.close()
