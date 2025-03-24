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

if __name__ == "__main__":
    """
    Main entry point for the SIGAAMOS bot application.
    Initializes the database and bot, registers handlers, and starts the bot.
    """
    db_handler = Database('sqlite:///avisos.db')
    bot = SIGAAMOS_bot(TOKEN, db_handler).use_default_handlers()
    bot.register_handlers()
    bot.run()