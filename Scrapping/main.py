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

from App import App

if __name__ == "__main__":
    app = App()
    app.setup(TOKEN)
    app.run()
    app.close()
    
