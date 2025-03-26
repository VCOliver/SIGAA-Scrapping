from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Chat(Base):
    """
    Represents a chat entity in the database.

    Attributes:
        chat_id (int): The primary key of the chat.
        items (list[Item]): A list of items associated with the chat, 
            ordered by the `item_id` of each item. This establishes a 
            one-to-many relationship with the `Item` model.
    """
    __tablename__ = 'chats'
    chat_id = Column(Integer, primary_key=True)
    items = relationship("Item", order_by='Item.item_id', back_populates="chat")

class Item(Base):
    """
    Represents an item in the database.

    Attributes:
        __tablename__ (str): The name of the database table ('items').
        item_id (int): The primary key of the item, auto-incremented.
        chat_id (int): The foreign key referencing the 'chats' table, linking the item to a specific chat.
        item_data (str): A unique string representing subject class to be searched.
        chat (Chat): A relationship to the Chat model, allowing access to the associated chat object.
    """
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)
    item_data = Column(String, nullable=False, unique=True)
    chat = relationship("Chat", back_populates="items")

class Subject(Base):
    """
    Represents a subject in the database.

    Attributes:
        id (int): The primary key of the subject, auto-incremented.
        subject (str): The name of the subject.
        codigo (str): A unique code identifying the subject.
        classes (list): A relationship to the `Class_info` model, representing the classes
            associated with this subject. The relationship is ordered by the `id` of `Class_info`.
    """
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String)
    codigo = Column(String, unique=True, nullable=False)
    classes = relationship("Class_info", order_by="Class_info.id", back_populates="subject")

class Class_info(Base):
    """
    Represents information about a class in the database.

    Attributes:
        id (int): The primary key of the class, auto-incremented.
        codigo (str): The code of the subject associated with the class. 
                      This is a foreign key referencing the 'subjects.codigo' column.
        N_o (str) : Number of the class
        ano_periodo (str): The year and period of the class (e.g., "2023.1").
        docente (str): The name of the instructor or professor teaching the class.
        horario (str): The schedule of the class (e.g., "Mon 10:00-12:00").
        vagas_ofertadas (int): The total number of seats offered in the class.
        vagas_ocupadas (int): The number of seats currently occupied in the class.
        vagas_disponiveis (int): The number of seats still available in the class.
        local (str): The location where the class is held (e.g., "Room 101").
        subject (Subject): The relationship to the Subject model, representing the subject 
                           associated with this class. This is a back-populated relationship.
    """
    __tablename__ = "class_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, ForeignKey('subjects.codigo'), nullable=False)
    N_o = Column(String)
    ano_periodo = Column(String)
    docente = Column(String)
    horario = Column(String)
    vagas_ofertadas = Column(Integer)
    vagas_ocupadas = Column(Integer)
    vagas_disponiveis = Column(Integer)
    local = Column(String)
    __table_args__ = (UniqueConstraint('N_o', 'codigo', 'docente', 'ano_periodo', 'horario', name='_info_uc'),)
    subject = relationship("Subject", back_populates="classes")