import psycopg2
from utils.logger import logger


class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(self.config)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logger.debug("Connection with database ended.")

    def insert_books(self, books):
        with self.connection.cursor() as cursor:
            cursor.executemany(
                """INSERT INTO books_book(slug, title, author, url, price, image, status, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT DO NOTHING""",
                (books),
            )
        self.connection.commit()
