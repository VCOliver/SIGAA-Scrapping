from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Chat(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, primary_key=True)

class Item(Base):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)
    item_data = Column(String, nullable=False, unique=True)
    chat = relationship("Chat", back_populates="items")

Chat.items = relationship("Item", order_by=Item.item_id, back_populates="chat")

class Database:
    """Database handler for managing chat and item data."""

    def __init__(self, db_url: str):
        """
        Initialize the database connection and create tables if they don't exist.
        
        :param db_url: URL to the SQLite database.
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_chat(self, chat_id):
        """
        Add a chat to the chats table.
        
        :param chat_id: ID of the chat.
        """
        session = self.Session()
        chat = Chat(chat_id=chat_id)
        session.add(chat)
        session.commit()
        session.close()

    def add_item(self, chat_id, item):
        """
        Add an item linked to a chat.
        
        :param chat_id: ID of the chat.
        :param item: Name of the subject to warn about.
        """
        session = self.Session()
        item = Item(chat_id=chat_id, item_data=item)
        session.add(item)
        session.commit()
        session.close()

    def close(self):
        """Close the database connection."""
        self.engine.dispose()