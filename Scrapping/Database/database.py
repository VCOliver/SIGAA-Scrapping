from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import pandas as pd

from .models import Base, Chat, Item, Subject, Class_info

from typing import Final, Self

class Database:
    """Database handler for managing chat, item, subject, and class information data."""
    
    USER_DB: Final = "sqlite:///chats.db"
    CLASSES_DB: Final = "sqlite:///classes.db"

    def __init__(self):
        """
        Initialize the database connections and create tables if they don't exist.
        
        This method sets up two SQLite databases: one for user-related data (chats and items)
        and another for class-related data (subjects and class information).
        """
        self._user_engine = create_engine(self.USER_DB)
        self._class_engine = create_engine(self.CLASSES_DB)
        Base.metadata.create_all(self._user_engine)
        Base.metadata.create_all(self._class_engine)
        self._userSession = sessionmaker(bind=self._user_engine)
        self._classSession = sessionmaker(bind=self._class_engine)
        
    def create(self, data: list[dict]) -> Self:
        from pathlib import Path
        
        """
        Check if the database files exist. If not, create them and populate with the provided data.
        
        :param data: List of dictionaries containing the data to populate the database.
        """
        user_db_path = Path(self.USER_DB.replace("sqlite:///", ""))
        classes_db_path = Path(self.CLASSES_DB.replace("sqlite:///", ""))
        
        try:
            for class_info in data:
                subject = {
                    "Matéria": class_info["Matéria"],
                    "Código": class_info["Código"]
                }
                self._add_classes(subject, class_info)
                
            print("Data saved in database")
        except Exception as e:
            print(e)
        finally:
            self.close()
            return self
            

    def add_chat(self, chat_id):
        """
        Add a chat to the chats table in the user database if it doesn't already exist.
        
        :param chat_id: ID of the chat to be added.
        """
        session = self._userSession()
        try:
            # Check if the chat_id already exists
            existing_chat = session.query(Chat).filter_by(chat_id=chat_id).first()
            if not existing_chat:
                chat = Chat(chat_id=chat_id)
                session.add(chat)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding chat: {e}")
        finally:
            session.close()

    def add_item(self, chat_id, item_data):
        """
        Add an item linked to a specific chat in the user database.
        
        :param chat_id: ID of the chat to which the item is linked.
        :param item_data: Data of the item to be added.
        """
        session = self._userSession()
        item = Item(chat_id=chat_id, item_data=item_data)
        session.add(item)
        session.commit()
        session.close()
        
    def _add_classes(self, subject: dict, class_info: dict):
        """
        Add subject and class information to the classes database.
        
        :param subject: Dictionary containing the subject name and code.
        :param class_info: Dictionary containing class information
            (year_semester, teacher, schedule, offered_vacancies, occupied_vacancies,
            available_vacancies, location).
        """
        self._add_subject(subject["Matéria"], subject["Código"])
        self._add_classes_info(subject["Código"], class_info["N_o"], class_info["Ano-Período"], class_info["Docente"], 
                               class_info["Horário"], class_info["Qtde Vagas Ofertadas"], 
                               class_info["Qtde Vagas Ocupadas"], class_info["Qtde Vagas Disponíveis"], 
                               class_info["Local"]
                            )        
        
    def _add_subject(self, name: str, code: str):
        """
        Add a subject to the subjects table in the classes database if it doesn't already exist.
        
        :param name: Name of the subject.
        :param code: Unique code of the subject.
        """
        session = self._classSession()
        try:
            # Attempt to add the subject directly
            subject = Subject(subject=name, codigo=code)
            session.add(subject)
            session.commit()
        except IntegrityError:
            # If the subject already exists, rollback the session
            session.rollback()
        finally:
            session.close()
        
    def _add_classes_info(self, subject_code: str, class_number:str, year_semester: str, teacher: str, schedule: str, 
                          offered_vacancies: int, occupied_vacancies: int, available_vacancies: int, location: str):
        """
        Add class information to the classes table in the classes database.
        
        :param subject_code: Code of the subject associated with the class.
        :param year_semester: Year and semester of the class (e.g., "2023.1").
        :param teacher: Name of the teacher for the class.
        :param schedule: Schedule of the class.
        :param offered_vacancies: Total number of offered vacancies.
        :param occupied_vacancies: Number of occupied vacancies.
        :param available_vacancies: Number of available vacancies.
        :param location: Location where the class is held.
        """
        if not all(isinstance(arg, int) for arg in [offered_vacancies, occupied_vacancies, available_vacancies]):
            try:
                offered_vacancies = int(offered_vacancies)
                occupied_vacancies = int(occupied_vacancies)
                available_vacancies = int(available_vacancies)
            except ValueError:
                raise ValueError("offered_vacancies, occupied_vacancies, and available_vacancies must be integers.")
        
        session = self._classSession()
        try:
            class_info = Class_info(codigo=subject_code, 
                                    N_o=class_number,
                                    ano_periodo=year_semester, 
                                    docente=teacher, 
                                    horario=schedule, 
                                    vagas_ofertadas=offered_vacancies, 
                                    vagas_ocupadas=occupied_vacancies, 
                                    vagas_disponiveis=available_vacancies, 
                                    local=location)
            session.add(class_info)
            session.commit()
        except IntegrityError as e:
            session.rollback()
        finally:
            session.close()
            
    def filter(self, by: str = 'availability') -> pd.DataFrame:
        """
        Filters and retrieves class information from the database based on the specified criteria.
        Args:
            by (str, optional): The filtering criterion. Defaults to 'availability'.
                - 'availability': Filters by available spots and excludes 'offered_spots' and 'occupied_spots' columns.
                - 'occupied': Filters by occupied spots and excludes 'offered_spots' and 'available_spots' columns.
                - 'offered': Filters by offered spots and excludes 'available_spots' and 'occupied_spots' columns.
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the filtered class information with the following columns:
                - subject: The name of the subject.
                - code: The code of the class.
                - num: The class number.
                - period: The year and period of the class.
                - professor: The name of the professor teaching the class.
                - schedule: The schedule of the class.
                - available_spots/offered_spots/occupied_spots: The number of spots based on the filter.
                - local: The location of the class.
        Raises:
            Exception: Prints the exception message if an error occurs during the query or data processing.
        """
        try:
            # Retrieve all data using get_df
            df = self.get_df()

            # Drop columns based on the filter criterion
            if by == 'availability':
                df = df[df["available_spots"] > 0]
                df.drop(columns=["offered_spots", "occupied_spots"], inplace=True)
            elif by == 'occupied':
                df.drop(columns=["offered_spots", "available_spots"], inplace=True)
            elif by == 'offered':
                df.drop(columns=["available_spots", "occupied_spots"], inplace=True)                

            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
            
    def get_df(self) -> pd.DataFrame:
        """
        Queries the database and returns all class information as a Pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing all class information with the following columns:
                - subject: The name of the subject.
                - code: The code of the class.
                - num: The class number.
                - period: The year and period of the class.
                - professor: The name of the professor teaching the class.
                - schedule: The schedule of the class.
                - offered_spots: The total number of offered spots.
                - occupied_spots: The number of occupied spots.
                - available_spots: The number of available spots.
                - local: The location of the class.
        """
        session = self._classSession()
        df = pd.DataFrame()

        try:
            # Query the database to join Class_info and Subject tables
            query = (
                session.query(Class_info, Subject)
                .join(Subject, Class_info.codigo == Subject.codigo)
            )

            # Convert the query results to a list of dictionaries
            data = [
                {
                    "subject": subject.subject,
                    "code": class_info.codigo,
                    "num": class_info.N_o,
                    "period": class_info.ano_periodo,
                    "professor": class_info.docente,
                    "schedule": class_info.horario,
                    "offered_spots": class_info.vagas_ofertadas,
                    "occupied_spots": class_info.vagas_ocupadas,
                    "available_spots": class_info.vagas_disponiveis,
                    "local": class_info.local,
                }
                for class_info, subject in query
            ]

            # Convert the data to a Pandas DataFrame
            df = pd.DataFrame(data)
        except Exception as e:
            print(e)
        finally:
            session.close()
            return df

    @property
    def sessions(self) -> tuple[sessionmaker[Session], sessionmaker[Session]]:
        """
        Provides access to the sessionmakers for user and class sessions.

        Returns:
            tuple[sessionmaker[Session], sessionmaker[Session]]: A tuple containing
            the sessionmaker instances for user and class sessions, respectifully.
        """
        return self._userSession, self._classSession
        
    def close(self):
        """
        Close the database connections.
        
        This method disposes of the engines for both the user and classes databases.
        """
        self._user_engine.dispose()
        self._class_engine.dispose()

    def update_classes(self, data: list[dict]):
        """
        Update the classes data in the database based on the provided data.

        :param data: List of dictionaries containing the updated class information.
        """
        session = self._classSession()
        try:
            for class_info in data:
                # Update or insert the subject
                subject = session.query(Subject).filter_by(codigo=class_info["Código"]).first()
                if not subject:
                    subject = Subject(subject=class_info["Matéria"], codigo=class_info["Código"])
                    session.add(subject)
                    session.commit()

                # Update or insert the class information
                class_record = session.query(Class_info).filter_by(
                    codigo=class_info["Código"],
                    N_o=class_info["N_o"],
                    ano_periodo=class_info["Ano-Período"],
                    docente=class_info["Docente"],
                    horario=class_info["Horário"]
                ).first()

                if class_record:
                    # Update existing record
                    class_record.vagas_ofertadas = class_info["Qtde Vagas Ofertadas"]
                    class_record.vagas_ocupadas = class_info["Qtde Vagas Ocupadas"]
                    class_record.vagas_disponiveis = class_info["Qtde Vagas Disponíveis"]
                    class_record.local = class_info["Local"]
                else:
                    # Insert new record
                    new_class = Class_info(
                        codigo=class_info["Código"],
                        N_o=class_info["N_o"],
                        ano_periodo=class_info["Ano-Período"],
                        docente=class_info["Docente"],
                        horario=class_info["Horário"],
                        vagas_ofertadas=class_info["Qtde Vagas Ofertadas"],
                        vagas_ocupadas=class_info["Qtde Vagas Ocupadas"],
                        vagas_disponiveis=class_info["Qtde Vagas Disponíveis"],
                        local=class_info["Local"]
                    )
                    session.add(new_class)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error updating classes: {e}")
        finally:
            session.close()

    def get_watched_items(self) -> list[tuple[int, str]]:
        """
        Retrieve all watched items and their associated chat IDs.

        Returns:
            list[tuple[int, str]]: A list of tuples containing chat IDs and subject codes.
        """
        session = self._userSession()
        try:
            query = session.query(Item.chat_id, Item.item_data).all()
            return [(chat_id, item_data) for chat_id, item_data in query]
        except Exception as e:
            print(f"Error retrieving watched items: {e}")
            return []
        finally:
            session.close()

    def remove_item(self, chat_id: int, subject_code: str) -> None:
        """
        Remove an item associated with a chat_id and subject_code from the database.

        Args:
            chat_id (int): The ID of the chat.
            subject_code (str): The code of the subject to remove.
        """
        session = self._userSession()
        try:
            item = session.query(Item).join(Chat).filter(
                Chat.chat_id == chat_id,
                Item.item_data == subject_code
            ).first()
            if item:
                session.delete(item)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error removing item: {e}")
        finally:
            session.close()