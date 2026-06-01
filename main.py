from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, init_db, Product, Order, Customer

app = FastAPI(title="Clothing Company")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    init_db()
    db = next(get_db())
    if not db.query(Product).first():
        products = [
            Product(name="Erkaklar ko'ylagi", category="Erkaklar", price=45000, stock=150),
            Product(name="Ayollar ko'ylagi", category="Ayollar", price=55000, stock=200),
            Product(name="Bolalar shimi", category="Bolalar", price=35000, stock=100),
            Product(name="Erkaklar shimi", category="Erkaklar", price=65000, stock=80),
            Product(name="Ayollar yubkasi", category="Ayollar", price=75000, stock=120),
        ]
        db.add_all(products)
        db.commit()
    if not db.query(Order).first():
        orders = [
            Order(customer="Alisher Karimov", product="Erkaklar ko'ylagi", quantity=10, status="Yetkazildi"),
            Order(customer="Malika Yusupova", product="Ayollar ko'ylagi", quantity=5, status="Jarayonda"),
            Order(customer="Sardor Toshmatov", product="Bolalar shimi", quantity=20, status="Kutilmoqda"),
        ]
        db.add_all(orders)
        db.commit()
    if not db.query(Customer).first():
        customers = [
            Customer(name="Alisher Karimov", city="Toshkent", orders=15, total=675000),
            Customer(name="Malika Yusupova", city="Samarqand", orders=8, total=440000),
            Customer(name="Sardor Toshmatov", city="Buxoro", orders=12, total=420000),
        ]
        db.add_all(customers)
        db.commit()

# --- Bosh sahifa ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_products": db.query(Product).count(),
            "total_orders": db.query(Order).count(),
            "total_customers": db.query(Customer).count()
        }
    )

# --- Mahsulotlar ---
@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"products": products}
    )

@app.post("/products/add")
async def add_product(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    db: Session = Depends(get_db)
):
    product = Product(name=name, category=category, price=price, stock=stock)
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303)

@app.get("/products/delete/{id}")
async def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/products", status_code=303)

# --- Buyurtmalar ---
@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={"orders": orders}
    )

@app.post("/orders/add")
async def add_order(
    customer: str = Form(...),
    product: str = Form(...),
    quantity: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    order = Order(customer=customer, product=product, quantity=quantity, status=status)
    db.add(order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)

@app.get("/orders/delete/{id}")
async def delete_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if order:
        db.delete(order)
        db.commit()
    return RedirectResponse(url="/orders", status_code=303)

# --- Mijozlar ---
@app.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={"customers": customers}
    )

@app.post("/customers/add")
async def add_customer(
    name: str = Form(...),
    city: str = Form(...),
    db: Session = Depends(get_db)
):
    customer = Customer(name=name, city=city, orders=0, total=0)
    db.add(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)

@app.get("/customers/delete/{id}")
async def delete_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)