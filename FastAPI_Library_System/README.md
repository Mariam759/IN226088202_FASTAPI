# 📚 Library Management API

## 📖 About the Project
This project is a backend system built using FastAPI as part of internship training. It simulates a real-world library system where users can view books, borrow them, manage returns, and track activity.

The goal of this project was to apply concepts like API design, validation, workflows, and data handling in a real-world scenario.

---

## 🎯 What This Project Does
- View all books in the library
- Get details of a specific book
- Borrow a book with validation
- Track borrow records
- Return a book and auto-assign to next user in queue
- Add books to a waiting queue
- Search, filter, and sort books
- Pagination for large datasets
- Browse books using combined search, sort, and pagination

---

## 🚀 Technologies Used
- Python  
- FastAPI  
- Pydantic  
- Uvicorn  

---

## 📁 Project Structure
# 📚 Library Management API

## 📖 About the Project
This project is a backend system built using FastAPI as part of internship training. It simulates a real-world library system where users can view books, borrow them, manage returns, and track activity.

The goal of this project was to apply concepts like API design, validation, workflows, and data handling in a real-world scenario.

---

## 🎯 What This Project Does
- View all books in the library
- Get details of a specific book
- Borrow a book with validation
- Track borrow records
- Return a book and auto-assign to next user in queue
- Add books to a waiting queue
- Search, filter, and sort books
- Pagination for large datasets
- Browse books using combined search, sort, and pagination

---

## 🚀 Technologies Used
- Python  
- FastAPI  
- Pydantic  
- Uvicorn  

---

## 📁 Project Structure
FastAPI_Library_System/
│── main.py
│── requirements.txt
│── README.md
└── screenshots/


---

📌 Key Features Implemented
✅ Core APIs
GET APIs for retrieving books and records
POST APIs with Pydantic validation
✅ CRUD Operations
Add new book
Update book details
Delete book (with business rule: cannot delete borrowed book)
✅ Helper Functions
find_book() → find book by ID
calculate_due_date() → calculate return date
filter_books_logic() → filter books
✅ Multi-Step Workflow
Borrow → Queue → Return & Auto-Assign
✅ Borrow System Features
Book availability check
Member validation
Due date calculation
Premium vs Regular member logic
✅ Queue System
Add users to queue when book unavailable
Automatically assign book when returned
✅ Advanced Features
Search books (title & author)
Sort books (title, author, genre)
Pagination
Combined /books/browse endpoint
