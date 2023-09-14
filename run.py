from text_unidecode import unidecode
from utils.logger import logger

from app import get_books

books = get_books(start_page=0, end_page=5)


def print_by_title() -> None:
    logger.info("Listing books by title...")
    books_by_title = sorted(books, key=lambda x: unidecode(x.title))
    for book in books_by_title:
        print(
            f"{book.title} - {book.author} ({book.price}) - description: {book.description[:30]}"
        )


def print_by_author() -> None:
    logger.info("Listing books by author...")
    books_by_author = sorted(books, key=lambda x: unidecode(x.author))
    for book in books_by_author:
        print(
            f"{book.author} - {book.title} ({book.price}) - description: {book.description[:30]}"
        )


def print_by_price() -> None:
    logger.info("Listing books by price... (cheapest first)")
    books_by_price = sorted(books, key=lambda x: x.price)
    for book in books_by_price:
        print(
            f"{book.author} - {book.title} ({book.price} €) - description: {book.description[:30]}"
        )


def search_book() -> None:
    logger.info("Searching for book by title of an author...")
    search_word = input(
        "Write the exact title or name of an author to get book details: "
    )
    found_books = [book for book in books if search_word in (book.title, book.author)]
    if found_books:
        for book in found_books:
            _print_details(book)
    else:
        print("No book found!")


# Book generator
nbook = (book for book in books)


def next_book() -> None:
    logger.info("Listing next book...")
    _print_details(next(nbook))


def _print_details(book):
    print(
        f"""******************************Book Details******************************
Title: {book.title}
Author: {book.author}
URL link: {book.url}
Price: {book.price} €
Availability: {book.status}
Description: {book.description}
********************************************************************"""
    )


choices: dict = {
    "title": print_by_title,
    "author": print_by_author,
    "price": print_by_price,
    "search": search_book,
    "next": next_book,
}


def main() -> None:
    # Basic page input

    # mutliple pages check
    while True:
        single_page_input = input(
            "Do you want to scrape elements only from one page? (Y/n): "
        ).lower()
        if single_page_input == "y":
            url = input("What website do you want to scrape? ")
            end_page = 0
            break
        elif single_page_input == "n":
            url = input(
                "What website do you want to scrape? (It is the webpage with numuerous elements you want to scrape usualy ending as '/p=' or '/page/' without the last number): "
            )
            end_page = int(
                input("From how many pages do you want to scrape elements? ")
            )
            break
        else:
            print("You must type Y for 'yes' or n for 'no'!")

    with open("locators/pageLocator.py", "w") as file:
        file.write(f'class PageLocator:\n    PAGE = "{url}"\n')

    # getting preview
    response = requests.get(url + "0" if end_page != 0 else url)
    if response_check(response):
        page = BeautifulSoup(response.content, "html.parser")
        elementLocator = input("Provide html tags as locator for a tag of element: ")

        url_property = property_check()
        with open("locators/pageLocator.py", "a") as file:
            file.write(
                f'    ELEMENT = "{elementLocator}"\n    URL_PROPERTY = "{url_property}"'
            )

        elementUrl = page.select(elementLocator)
        print(elementUrl[0])
        url = elementUrl[0][url_property] if url_property else elementUrl[0]
        print(url)


#     while True:
#         choice = input(
#             """
# Choose an order in which you want to present scraped books:
# - by title: "title"
# - by author: "author"
# - by price: "price"
# To search for a book: "search"
# To show details of a next book: "next"
# To quit: "quit"
# >> """
#         )
#         if choice == "quit":
#             logger.debug("Terminating the program...")
#             break
#         elif choice in choices:
#             choices[choice]()
#         else:
#             print("Unrecognized order! Try again!")


if __name__ == "__main__":
    main()
