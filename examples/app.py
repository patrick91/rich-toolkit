import asyncio
import json
from typing import Any, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing_extensions import Annotated

app = FastAPI()

db: List[Any] = []


# Pydantic model for a Book
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    year: int


# Dependency for getting a book by ID
def get_book_by_id(book_id: int):
    book = next((book for book in db if book.id == book_id), None)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books/", response_model=Book)
def create_book(book: Book):
    book.id = len(db) + 1
    db.append(book)
    return book


@app.get("/books/", response_model=List[Book])
def read_books():
    print(1 / 0)
    return db


BookDependency = Annotated[Book, Depends(get_book_by_id)]


@app.get("/books/{book_id}", response_model=Book)
def read_book(book: BookDependency):
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(updated_book: Book, book: BookDependency):
    book.title = updated_book.title
    book.author = updated_book.author
    book.year = updated_book.year
    return book


@app.delete("/books/{book_id}", response_model=Book)
def delete_book(book: BookDependency):
    db.remove(book)
    return book


@app.get("/stream/")
async def stream_data():
    async def generate():
        for i in range(10):
            data = {"item": i + 1, "message": f"Streaming item {i + 1}"}
            yield json.dumps(data) + "\n"
            await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
