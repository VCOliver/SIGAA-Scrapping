# Creating Bot class
import asyncio
from typing import Self
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from Database import Database
from asyncio import sleep  # Import sleep for periodic checks

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
        if not query:
            await update.message.reply_text("Por favor, use /search <código da matéria>.")
            return

        # Query the database for the subject code
        result = self.db.get_df()
        if query not in result['code'].values:
            await update.message.reply_text(
            "Nenhuma matéria com esse código foi encontrada."
            "Por favor, confira se o código foi escrito corretamente.\n\n"
            "Por enquanto, sou capaz apenas de pesquisar por classes na FCTE do Gama."
            )
            return
        result = self.db.filter(by='availability')
        filtered_result = result[result['code'] == query]

        if filtered_result.empty:
            response = f"Nenhuma sala de {query} encontrada com vagas disponíveis."
            
        else:
            response = ""
            for _, row in filtered_result.iterrows():
                response += (
                    f"{row['available_spots']} vagas encontradas para {row['subject']} turma {row['num']} "
                    f"com {row['professor']} no horário {row['schedule']} "
                    f"{row['local']} para o semestre {row['period']}.\n\n"
                )

        await update.message.reply_text(response)
        
    def _save_warning(self, chat_id: int, subject_code: str):
        """
        Save a warning to the database.
        
        :param chat_id: ID of the chat.
        :param item: Data of the item.
        """
        if not chat_id or not subject_code:
            return
        self.db.add_chat(chat_id)
        self.db.add_item(chat_id, subject_code)
    
    async def _warn_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /warn command.
        
        :param update: Update instance.
        :param context: Context instance.
        """
        import re  # Import regex module for pattern matching

        chat_id = update.effective_chat.id
        query = ' '.join(context.args).upper().strip()

        # Check if query matches the format of 3 or 4 letters followed by 4 numbers
        if not re.match(r'^[A-Za-z]{3,4}\d{4}$', query):
            await update.message.reply_text(
                "O código da matéria deve estar no formato de 3 ou 4 letras seguidas de 4 números. "
                "Por exemplo: FCTE1234 ou FGA2345."
            )
            return

        self._save_warning(chat_id, query)  # Save the warning to the database
        await update.message.reply_text(f"Vou te avisar quando {query} estiver livre")
        
    async def _notify_users(self):
        """
        Check the database for updates and notify users if their watched subjects have available spots.
        """
        watched_items = self.db.get_watched_items()
        for chat_id, subject_code in watched_items:
            result = self.db.filter(by='availability')
            filtered_result = result[result['code'] == subject_code]

            if not filtered_result.empty:
                response = ""
                for _, row in filtered_result.iterrows():
                    response += (
                        f"{row['available_spots']} vagas encontradas para {row['subject']} turma {row['num']} "
                        f"com {row['professor']} no horário {row['schedule']} "
                        f"{row['local']} para o semestre {row['period']}.\n\n"
                    )
                await self.bot.bot.send_message(chat_id=chat_id, text=response)

    async def _periodic_check(self):
        """
        Periodically check for updates in the database and notify users.
        """
        while True:
            await self._notify_users()
            await sleep(60*10)  # Wait for 10 minutes

    def run(self):
        """Start the bot and begin polling for updates."""
        print("Bot is running...")
        loop = asyncio.get_event_loop()  # Get the current event loop
        loop.create_task(self._periodic_check())  # Schedule periodic checks
        self.bot.run_polling(poll_interval=3)
        
    @property
    def handlers(self) -> list[CommandHandler]:
        """Get the list of command handlers."""
        return self.__handlers