import sys
from utils.logger import logger
from db.database import Database

from app import get_books


def main() -> None:
    try:
        from db_config.database_config import get_database_config

        db_config = get_database_config()
    except Exception as e:
        logger.error(f"Error reading database config file: {str(e)}")
        sys.exit(1)

    num_of_pages = int(input("How many pages do you want to scrape? "))
    for i in range(num_of_pages // 10 + 1):
        start_page = i * 10 + 1
        end_page = i * 10 + 10
        books = get_books(start_page, end_page)
        try:
            database = Database(db_config)
            database.connect()
            logger.debug("Connection with database created")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            sys.exit(1)

        try:
            logger.debug(
                f"Adding books of pages {start_page} - {end_page} to database..."
            )
            database.insert_books(
                (
                    (
                        book.slug,
                        book.title,
                        book.author,
                        book.url,
                        book.price,
                        book.image,
                        book.status,
                        book.description,
                    )
                    for book in books
                )
            )
            logger.info(
                f"Books of pages {start_page} - {end_page} added into database..."
            )
        except Exception as e:
            logger.error(
                f"Error processing books of pages {start_page} - {end_page}: {str(e)}"
            )

        # Disconnect database
        database.disconnect()


if __name__ == "__main__":
    main()
