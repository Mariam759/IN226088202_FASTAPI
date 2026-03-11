from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List

app = FastAPI()

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
    delivery_address: str = Field(..., min_length=10)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)
    
# ── Temporary data acting as our database ─────────────────────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand', 'price': 399, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 699, 'category': 'Electronics', 'in_stock': False},
    {'id': 7, 'name': 'Webcam', 'price': 999, 'category': 'Electronics', 'in_stock': True},
]

orders = []
feedback = []
order_counter = 1


# ── Home ─────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


# ── Get all products ─────────────────────────────
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# ── Filter products ─────────────────────────────
@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):
    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "count": len(result)}


# ── In-stock products ────────────────────────────
@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": in_stock_products,
        "count": len(in_stock_products)
    }


# ── Deals (cheapest + most expensive) ───────────
@app.get("/products/deals")
def get_product_deals():

    cheapest_product = min(products, key=lambda p: p["price"])
    most_expensive_product = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest_product,
        "premium_pick": most_expensive_product
    }


# ── Category filter ─────────────────────────────
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered_products = [p for p in products if p["category"] == category_name]

    if not filtered_products:
        return {"error": "No products found in this category"}

    return {"products": filtered_products}


# ── Search products ─────────────────────────────
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = [
        p for p in products if keyword.lower() in p["name"].lower()
    ]

    if not matched_products:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "count": len(matched_products)
    }


# ── Store summary ───────────────────────────────
@app.get("/store/summary")
def store_summary():

    total_products = len(products)
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }


# ── Get product price only ──────────────────────
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# ── Product Summary Dashboard ─────────────────────
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])

    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    cheapest = min(products, key=lambda p: p["price"])

    most_expensive = max(products, key=lambda p: p["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


# ── Get product by ID ───────────────────────────
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    return {"error": "Product not found"}

# ── Feedback Endpoint ───────────────────────────
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }


# ──Single Order Endpoint ───────────────────────────
@app.post("/orders")
def place_order(order_data: OrderRequest):

    global order_counter

    product = next((p for p in products if p["id"] == order_data.product_id), None)

    if product is None:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    total_price = product["price"] * order_data.quantity

    order = {
        "order_id": order_counter,
        "customer_name": order_data.customer_name,
        "product": product["name"],
        "quantity": order_data.quantity,
        "delivery_address": order_data.delivery_address,
        "total_price": total_price,
        "status": "pending"
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order placed successfully", "order": order}

# ──Order ID Endpoint ───────────────────────────
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}

# ──Order ID confirming Endpoint ───────────────────────────
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}

# ──bulk Order Endpoint ───────────────────────────
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if product is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

        grand_total += subtotal

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
