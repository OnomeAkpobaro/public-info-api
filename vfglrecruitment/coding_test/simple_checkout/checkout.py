from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="Skill Test E-commerce API")

# In-memory storage (for testing purposes)
users_db = {}
products_db = [
    {"id": "1", "name": "Wireless Headphones", "price": 79.99, "category": "electronics", "stock": 50},
    {"id": "2", "name": "Running Shoes", "price": 89.99, "category": "sports", "stock": 30},
    {"id": "3", "name": "Coffee Maker", "price": 49.99, "category": "home", "stock": 20},
    {"id": "4", "name": "Laptop Stand", "price": 34.99, "category": "electronics", "stock": 40},
    {"id": "5", "name": "Yoga Mat", "price": 24.99, "category": "sports", "stock": 60},
]
categories_db = ["electronics", "sports", "home", "clothing", "books"]
orders_db = {}

# ============ MODELS ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token: str
    user: dict

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    shipping_address: str
    email: EmailStr

class CheckoutResponse(BaseModel):
    order_id: str
    total: float
    status: str
    message: str

# ============ AUTHENTICATION ENDPOINTS ============

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(data: RegisterRequest):
    """Register a new user"""
    if data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    token = f"token_{user_id}"
    
    users_db[data.email] = {
        "id": user_id,
        "email": data.email,
        "name": data.name,
        "password": data.password  # In production, hash this!
    }
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": data.email,
            "name": data.name
        }
    }

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    """Login user"""
    user = users_db.get(data.email)
    
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = f"token_{user['id']}"
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }

# ============ CATEGORIES ENDPOINT ============

@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    return {
        "categories": categories_db
    }

@app.get("/api/categories/{category}/products")
async def get_products_by_category(category: str):
    """Get products by category"""
    if category not in categories_db:
        raise HTTPException(status_code=404, detail="Category not found")
    
    filtered_products = [p for p in products_db if p["category"] == category]
    return {
        "category": category,
        "products": filtered_products
    }

# ============ PRODUCTS ENDPOINTS ============

@app.get("/api/products")
async def get_products():
    """Get all products"""
    return {"products": products_db}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ============ CHECKOUT ENDPOINT ============

@app.post("/api/checkout", response_model=CheckoutResponse)
async def checkout(data: CheckoutRequest):
    """Process checkout"""
    
    # Validate items and calculate total
    total = 0
    order_items = []
    
    for item in data.items:
        product = next((p for p in products_db if p["id"] == item.product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        item_total = product["price"] * item.quantity
        total += item_total
        
        order_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "subtotal": item_total
        })
        
        # Update stock
        product["stock"] -= item.quantity
    
    # Create order
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "items": order_items,
        "total": total,
        "shipping_address": data.shipping_address,
        "email": data.email,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat()
    }
    
    orders_db[order_id] = order
    
    return {
        "order_id": order_id,
        "total": total,
        "status": "confirmed",
        "message": "Order placed successfully!"
    }

# ============ ORDER ENDPOINTS ============

@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ============ ROOT ============

@app.get("/")
async def root():
    """API Info"""
    return {
        "message": "Skill Test E-commerce API",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login"
            },
            "categories": {
                "list": "GET /api/categories",
                "products": "GET /api/categories/{category}/products"
            },
            "products": {
                "list": "GET /api/products",
                "detail": "GET /api/products/{id}"
            },
            "checkout": {
                "create": "POST /api/checkout",
                "order": "GET /api/orders/{id}"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)