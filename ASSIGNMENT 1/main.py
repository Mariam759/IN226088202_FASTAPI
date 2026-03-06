from fastapi import FastAPI , Query 

app = FastAPI()

# — Temporary data acting as our database for now —
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand', 'price': 399, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 699, 'category': 'Electronics', 'in_stock': False},
    {'id': 7, 'name': 'Webcam', 'price': 999, 'category': 'Electronics', 'in_stock': True},
]

# — Endpoint 0 – Home —
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# — Endpoint 1 – Return all products —
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}


@app.get('/products/filter')
def filter_products(
    category: str = Query(None, description='Electronics or Stationery'),
    max_price: int = Query(None, description='Maximum price'),
    in_stock: bool = Query(None, description='True = in stock only')
):
    result = products  # start with all products

    if category:
        result = [p for p in result if p['category'] == category]

    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return {'filtered_products': result, 'count': len(result)}


#-Endpoint 4-
@app.get("/products/instock")
def get_instock_products():
    in_stock_products = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": in_stock_products,
        "count": len(in_stock_products)
    }

# — Endpoint 7 – Cheapest & Most Expensive Product —
@app.get("/products/deals")
def get_product_deals():

    cheapest_product = min(products, key=lambda p: p["price"])
    most_expensive_product = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest_product,
        "premium_pick": most_expensive_product
    }

# — Endpoint 2 – Return one product by its ID —
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}

    return {'error': 'Product not found'}

# — Endpoint 3 —
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    
    filtered_products = [p for p in products if p["category"] == category_name]

    if not filtered_products:
        return {"error": "No products found in this category"}

    return {"products": filtered_products}

# — Endpoint 5 – Store Summary —
@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"] == True])

    out_of_stock_count = len([p for p in products if p["in_stock"] == False])

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }

# — Endpoint 6 – Search products by name —
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not matched_products:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "count": len(matched_products)
    }


