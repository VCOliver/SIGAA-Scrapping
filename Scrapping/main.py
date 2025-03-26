import os
from pathlib import Path

# Handling .env file
parent_dir = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(parent_dir, '.env')
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(f"File {dotenv_path} not found")

from typing import Final

TOKEN: Final = os.getenv("BOT_TOKEN")
print(TOKEN)

from Telegram.telegram_bot import SIGAAMOS_bot
from Database import Database
from SIGAA.scrapping import SIGAA_Scraper

if __name__ == "__main__":
    scraper = SIGAA_Scraper()
    scraper.access_portal()
    scraper.access_classes()
    data = scraper.update_classes_info(True)
    
    db = Database()
    db.create(data)
    scraper.quit()