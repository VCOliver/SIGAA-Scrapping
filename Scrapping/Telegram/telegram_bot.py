# Creating Bot class
from typing import Self
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from Database import Database

class SIGAAMOS_bot:
    """Telegram bot for managing SIGAA notifications."""

    def __init__(self, TOKEN: str, db_handler: Database):
        """
        Initialize the bot with the given token and database handler.
        
        :param TOKEN: Telegram bot token.
        :param db_handler: Instance of the Database class.
        """
        self.bot = ApplicationBuilder().token(TOKEN).build()
        self.db = db_handler
        
        self.__handlers: list[CommandHandler] = []
        
    def register_handlers(self) -> None:
        """Register all command handlers with the bot."""
        for handler in self.__handlers:
            self.bot.add_handler(handler)
        
    def use_default_handlers(self) -> Self:
        """Add default command handlers to the bot."""
        self.__handlers.append(CommandHandler("start", self._start_handler))
        self.__handlers.append(CommandHandler("search", self._search_handler))
        self.__handlers.append(CommandHandler("warn", self._warn_handler))
        
        return self
        
    def add_handler(self, handler: CommandHandler) -> None:
        """
        Add a custom command handler to the bot.
        
        :param handler: CommandHandler instance.
        """
        self.__handlers.append(handler)
        
    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /start command.
        
        :param update: Update instance.
        :param context: Context instance.
        """
        chat_id = update.effective_chat.id
        print(f'Conversation started with ID: {chat_id}')
        await update.message.reply_text("Salve fml! Sou um bot pra ajudar a pegar matérias na matricula Extraordinária")
        
    async def _search_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /search command.
        
        :param update: Update instance.
        :param context: Context instance.
        """
        query = ' '.join(context.args)
        await update.message.reply_text(f"Procurando por {query}")
        
    def _save_warning(self, chat_id: int, item: str):
        """
        Save a warning to the database.
        
        :param chat_id: ID of the chat.
        :param item: Data of the item.
        """
        if not chat_id or not item:
            return
        self.db.add_chat(chat_id)
        self.db.add_item(chat_id, item)
    
    async def _warn_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /warn command.
        
        :param update: Update instance.
        :param context: Context instance.
        """
        chat_id = update.effective_chat.id
        query = ' '.join(context.args)
        self._save_warning(chat_id, query)  # Save the warning to the database
        await update.message.reply_text(f"Vou te avisar quando {query} estiver livre")
        
    def run(self):
        """Start the bot and begin polling for updates."""
        print("Bot is running...")
        self.bot.run_polling(poll_interval=3)
        
    @property
    def handlers(self) -> list[CommandHandler]:
        """Get the list of command handlers."""
        return self.__handlers