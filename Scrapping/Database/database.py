import sqlite3
from sqlite3 import Error

class Database:
    """Database handler for managing chat and item data."""

    def __init__(self, db_path: str):
        """
        Initialize the database connection and create tables if they don't exist.
        
        :param db_path: Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create tables for chats and items."""
        
        sql_create_chats_table = """
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY
        );
        """

        sql_create_items_table = """
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            item_data TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
        );
        """

        try:
            self.cursor.execute(sql_create_chats_table)
            self.cursor.execute(sql_create_items_table)
            self.conn.commit()
        except Error as e:
            print(e)

    def add_chat(self, chat_id, /):
        """
        Add a chat to the chats table.
        
        :param chat_id: ID of the chat.
        """
        sql = "INSERT OR IGNORE INTO chats (chat_id) VALUES (?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (chat_id,))
        self.conn.commit()

    def add_item(self, chat_id, item, /):
        """
        Add an item linked to a chat.
        
        :param chat_id: ID of the chat.
        :param item: Name of the subject to warn about.
        """
        sql = "INSERT INTO items (chat_id, item_data) VALUES (?, ?)"
        cursor = self.conn.cursor()
        cursor.execute(sql, (chat_id, item))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()