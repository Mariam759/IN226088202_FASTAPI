from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from fastapi import Query

app = FastAPI()
queue = []

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    member_id: str = Field(..., min_length=4)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0)
    member_type: str = "regular"

def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None


def calculate_due_date(borrow_days, member_type):
    if member_type == "premium":
        max_days = 60
    else:
        max_days = 30

    if borrow_days > max_days:
        borrow_days = max_days

    return f"Return by: Day {15 + borrow_days}"

def filter_books_logic(genre=None, author=None, is_available=None):
    result = books

    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]

    if author is not None:
        result = [b for b in result if b["author"].lower() == author.lower()]

    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]

    return result

class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

books = [
    {"id": 1, "title": "Python Basics", "author": "John Doe", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "AI Revolution", "author": "Jane Smith", "genre": "Science", "is_available": True},
    {"id": 3, "title": "World History", "author": "Mark Lee", "genre": "History", "is_available": False},
    {"id": 4, "title": "Mystery Night", "author": "Agatha", "genre": "Fiction", "is_available": True},
    {"id": 5, "title": "Data Science 101", "author": "Andrew Ng", "genre": "Tech", "is_available": False},
    {"id": 6, "title": "Space Guide", "author": "Carl Sagan", "genre": "Science", "is_available": True}
]

borrow_records = []
record_counter = 1

@app.get("/books")
def get_books():
    total = len(books)
    available_count = len([b for b in books if b["is_available"]])

    return {
        "total_books": total,
        "available_books": available_count,
        "books": books
    }

@app.get("/books/summary")
def books_summary():
    total = len(books)
    available = len([b for b in books if b["is_available"]])
    borrowed = total - available

    genre_count = {}
    for book in books:
        genre = book["genre"]
        genre_count[genre] = genre_count.get(genre, 0) + 1

    return {
        "total": total,
        "available": available,
        "borrowed": borrowed,
        "genre_distribution": genre_count
    }

@app.get("/books/filter")
def filter_books(
    genre: str = Query(None),
    author: str = Query(None),
    is_available: bool = Query(None)
):
    filtered = filter_books_logic(genre, author, is_available)

    return {
        "count": len(filtered),
        "books": filtered
    }

@app.post("/borrow", status_code=status.HTTP_201_CREATED)
def borrow_book(request: BorrowRequest):
    global record_counter

    # Find book
    book = find_book(request.book_id)

    if not book:
        return {"error": "Book not found"}

    if not book["is_available"]:
        return {"error": "Book already borrowed"}

    # Mark book unavailable
    book["is_available"] = False

    # Calculate due date
    due_date = calculate_due_date(request.borrow_days, request.member_type)

    # Create record
    record = {
        "record_id": record_counter,
        "member_name": request.member_name,
        "member_id": request.member_id,
        "book_id": request.book_id,
        "due_date": due_date
    }

    borrow_records.append(record)
    record_counter += 1

    return {
        "message": "Book borrowed successfully",
        "data": record
    }

@app.get("/borrow-records")
def get_records():
    return {
        "total_records": len(borrow_records),
        "records": borrow_records
    }

@app.post("/books", status_code=201)
def add_book(book: NewBook):
    for b in books:
        if b["title"].lower() == book.title.lower():
            return {"error": "Book already exists"}

    new_id = max([b["id"] for b in books]) + 1

    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "is_available": book.is_available
    }

    books.append(new_book)

    return new_book

@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)

    if not book:
        return {"error": "Book not found"}

    if book["is_available"]:
        return {"message": "Book is available, no need to queue"}

    queue.append({
        "member_name": member_name,
        "book_id": book_id
    })

    return {"message": "Added to queue"}

@app.get("/queue")
def get_queue():
    return {"queue": queue}

@app.post("/return/{book_id}")
def return_book(book_id: int):
    global record_counter

    book = find_book(book_id)

    if not book:
        return {"error": "Book not found"}

    # Mark as available
    book["is_available"] = True

    # Check queue
    for i, q in enumerate(queue):
        if q["book_id"] == book_id:
            # Assign to next user
            book["is_available"] = False

            record = {
                "record_id": record_counter,
                "member_name": q["member_name"],
                "member_id": "AUTO",
                "book_id": book_id,
                "due_date": calculate_due_date(5, "regular")
            }

            borrow_records.append(record)
            record_counter += 1

            queue.pop(i)

            return {
                "message": "Returned and re-assigned",
                "new_record": record
            }

    return {"message": "Returned and available"}

@app.get("/books/search")
def search_books(keyword: str):
    keyword = keyword.lower()

    results = [
        b for b in books
        if keyword in b["title"].lower() or keyword in b["author"].lower()
    ]

    if not results:
        return {"message": "No books found"}

    return {
        "total_found": len(results),
        "books": results
    }

@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    valid_fields = ["title", "author", "genre"]

    if sort_by not in valid_fields:
        return {"error": "Invalid sort_by"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    sorted_books = sorted(books, key=lambda x: x[sort_by])

    if order == "desc":
        sorted_books.reverse()

    return {
        "sort_by": sort_by,
        "order": order,
        "books": sorted_books
    }

@app.get("/books/page")
def paginate_books(page: int = 1, limit: int = 3):
    total = len(books)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "books": books[start:end]
    }

@app.get("/borrow-records/search")
def search_records(member_name: str):
    results = [
        r for r in borrow_records
        if member_name.lower() in r["member_name"].lower()
    ]

    return {
        "total_found": len(results),
        "records": results
    }

@app.get("/borrow-records/page")
def paginate_records(page: int = 1, limit: int = 2):
    total = len(borrow_records)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "records": borrow_records[start:end]
    }

@app.get("/books/browse")
def browse_books(
    keyword: str = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = books

    # 🔍 FILTER (search)
    if keyword:
        keyword = keyword.lower()
        result = [
            b for b in result
            if keyword in b["title"].lower() or keyword in b["author"].lower()
        ]

    # 🔄 SORT
    if sort_by in ["title", "author", "genre"]:
        result = sorted(result, key=lambda x: x[sort_by])
        if order == "desc":
            result.reverse()

    # 📄 PAGINATION
    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "books": result[start:end]
    }

@app.put("/books/{book_id}")
def update_book(book_id: int, genre: str = None, is_available: bool = None):
    book = find_book(book_id)

    if not book:
        return {"error": "Book not found"}

    if genre is not None:
        book["genre"] = genre

    if is_available is not None:
        book["is_available"] = is_available

    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book["id"] == book_id:

            if not book["is_available"]:
                return {"error": "Cannot delete borrowed book"}

            deleted_title = book["title"]
            books.pop(i)
            return {"message": f"{deleted_title} deleted successfully"}

    return {"error": "Book not found"}

@app.get("/books/{book_id}") 
def get_book(book_id: int): 
    for book in books: 
        if book["id"] == book_id: 
            return book 
    return {"error": "Book not found"}
