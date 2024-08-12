from typing import Annotated

from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: int | None = None
    title: Annotated[str, Query(min_length=3)]
    author: Annotated[str, Query(min_length=1)]
    description: Annotated[str, Query(min_length=1, max_length=100)]
    rating: Annotated[int, Query(gt=0, lt=6)]
    published_date: Annotated[int, Query(le=2024)]

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'qwewwq',
                'description': 'A description of a new book',
                'rating': 5,
                'published_date': 2024
            }
        }


BOOKS = [
        Book(1, 'Computer Science Pro', 'qwewwq', 'A very nice book', 5, 2024),
        Book(2, 'Be fast with FastAPI', 'qwewwq', 'A great book', 5, 2020),
        Book(3, 'Master Endpoints', 'qwewwq', 'An awesome book', 5, 2022),
        Book(4, 'HP1', 'Author1', 'Book description', 2, 2010),
        Book(5, 'HP2', 'Author2', 'Book description', 3, 2014),
        Book(6, 'HP3', 'Author3', 'Book description', 1, 2005)
]


@app.get('/books', status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def read_book(book_id: Annotated[int, Path(ge=1)]):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='id not found')


@app.get('/books/', status_code=status.HTTP_200_OK)
async def filter_by_rating(rating: Annotated[int, Query(ge=1, le=5)]):
    books_to_show = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_show.append(book)
    return books_to_show


@app.get('/books/publish/', status_code=status.HTTP_200_OK)
async def filter_by_published_date(published_date: Annotated[int, Query(ge=2000, le=2024)]):
    books_to_show = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_show.append(book)
    return books_to_show


@app.post('/create_book', status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1

    return book


@app.put('/books/update_book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_to_update: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_to_update.id:
            new_book = Book(**book_to_update.dict())
            BOOKS[i] = new_book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='id not found')


@app.delete('/books/{book_to_delete_id}', status_code=status.HTTP_204_NO_CONTENT)
async def books_to_delete(book_to_delete_id: Annotated[int, Path(ge=1)]):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_to_delete_id:
            book_changed = True
            BOOKS.pop(i)
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='id not found')
