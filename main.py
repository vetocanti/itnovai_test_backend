from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from utils import models,crud,schemas,database
from typing import List
import threading
from fastapi.responses import JSONResponse
import logging
import traceback


app = FastAPI()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


models.database.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Clase para gestionar conexiones
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: dict):
#         for connection in self.active_connections:
#             await connection.send_json(message)

# manager = ConnectionManager()

# Endpoint para manejar WebSocket
# @app.websocket("/ws/cart")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             # Recibir datos del cliente
#             data = await websocket.receive_json()
#             print(f"Mensaje recibido: {data}")
#             # Ejemplo: manejar diferentes acciones
#             if data["action"] == "add_to_cart":
#                 response = {"message": "Producto añadido", "cart": data["cart"]}
#                 await manager.broadcast(response)
#             elif data["action"] == "remove_from_cart":
#                 response = {"message": "Producto eliminado", "cart": data["cart"]}
#                 await manager.broadcast(response)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         print("Cliente desconectado")
# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

#Products endpoints

# @app.get("/products/",response_model=schemas.ProductResponseModel)
# def get_products(db: Session = Depends(get_db), page: int = 0, limit: int = 10):
#     try
#         logger.info(f"Fetching products: page={page}, limit={limit}")
#         products = crud.get_products_by_pages(db, page, limit)
#         logger.info(f"Products fetched: {products}")
#         total_amount = crud.get_total_products_count(db)
#         logger.info(f"Total products count: {total_amount}")
#         product_models = [schemas.ProductModel(
#             id=product.id,
#             name=product.name,
#             price=product.price,
#             discount=product.discount,
#             url_image=product.url_image,
#             category_id=product.category_id,
#         ) for product in products]
#         return {
#             "page": page,
#             "limit": limit,
#             "total_amount": total_amount,
#             "records": product_models
#         }
#     except Exception as e:
#         print(f"Error fetching products: {e}")
#         traceback.print_exc()  # Agregar esto para más detalle
#         return JSONResponse(status_code=500, content={"error": "Error fetching products"})

@app.get("/products/", response_model=schemas.ProductResponseModel)
def get_products(db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    try:
        products = crud.get_products_by_pages(db, page, limit)
        total_amount = crud.get_total_products_count(db)
        product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
        return {
            "page": page,
            "limit": limit,
            "total_amount": total_amount,
            "records": product_models
        }
    except Exception as e:
        print(f"Error fetching products: {e}")
        return JSONResponse(status_code=500, content=e)

@app.get("/products_category/{category_id}", response_model=schemas.ProductResponseModel)
def get_products_by_category(db: Session = Depends(get_db), category_id: int=1, page: int=0, limit: int=10):
    try:
        products = crud.get_products_by_category(db, category_id, page, limit)
        total_amount = crud.get_total_products_count_by_category(db,category_id)
        product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]

        return {
            "page": page,
            "limit": limit,
            "total_amount": total_amount,
            "records": product_models
        }
    except Exception as e:
        print(f"Error fetching products: {e}")
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})
@app.get("/products_name/{name}", response_model=schemas.ProductResponseModel)
def get_product_by_name(name: str, db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    try: 
        products = crud.get_product_by_name(db, name, page, limit)
        total_amount = crud.get_total_products_count_by_name(db, name)
        products_model = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
        return {
            "page": page,
            "limit": limit,
            "total_amount": total_amount,
            "records": products_model
        }
    except Exception as e:
        print(f"Error fetching products: {e}")
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})




@app.get("/products_id/{id}", response_model=schemas.ProductModel)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        product = crud.get_product_by_id(db, id)
        return product
    except Exception as e:
        print(f"Error fetching product: {e}")
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})
thread = threading.Thread(target=crud.fetch_root_periodically)
thread.daemon = True
thread.start()

@app.get("/products_range/", response_model=schemas.ProductResponseModel)
def get_products_by_price(min_price: float , max_price: float , db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    try:
        products = crud.get_product_by_price_range(db, min_price, max_price, page, limit)
        total_amount = crud.get_total_products_count_by_price(db, min_price, max_price, limit, page)
        product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
        return {
            "page": page,
            "limit": limit,
            "total_amount": total_amount,
            "records": product_models,
        }
    except Exception as e:
        print(f"Error fetching products: {e}")
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})

@app.get("/products_discount/", response_model=schemas.ProductResponseModel)
def get_products_by_discount( db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    try:
        products = crud.get_products_with_discount(db, page, limit)
        total_amount = crud.get_products_with_discount_count(db)
        product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
        return {
            "page": page,
            "limit": limit,
            "total_amount": total_amount,
            "records": product_models,
        }
    except Exception as e:
        print(f"Error fetching products: {e}")
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})

@app.post("/products", response_model=schemas.ProductModel)  # Asegúrate de tener un modelo de respuesta definido
async def create_new_product(product_request: schemas.CreateProductRequest, db: Session = Depends(get_db)):
    # Verificar si ya existe un producto con el mismo nombre
    #existing_product = db.query(models.Product).filter(models.Product.name == product_request.name).first()
    #if existing_product:
    #    raise HTTPException(status_code=400, detail="Product already exists")

    # Crear el nuevo producto
    new_product = crud.create_product(db, product_request)

    if not new_product:
        raise HTTPException(status_code=500, detail="Error creating product")

    # Retornar el producto creado
    return new_product

@app.patch("/products/{product_id}", response_model=schemas.ProductModel)
async def update_product(product_id: int, product_request: schemas.UpdateProductRequest, db: Session = Depends(get_db)):
    # Verificar si el producto existe
    existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Actualizar los datos del producto
    updated_product = crud.update_product(db, product_id, product_request)

    if not updated_product:
        raise HTTPException(status_code=500, detail="Error updating product")

    # Retornar el producto actualizado
    return updated_product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    # Eliminar el producto por ID
    deleted_product = crud.delete_product(db, product_id)

    if not deleted_product:
        raise HTTPException(status_code=500, detail="Error deleting product")

    # Retornar mensaje de éxito
    return "Product deleted successfully"

#Categories endpoints

@app.get("/categories/", response_model=List[schemas.CategoryModel])
def get_categories(db: Session = Depends(get_db)):
    try:
        categories = crud.get_categories(db)
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return {"error": "Error fetching categories"}

@app.post("/categories", response_model=schemas.CategoryModel)
async def create_new_category(category_request: schemas.CreateCategoryRequest, db: Session = Depends(get_db)):
    # Verificar si ya existe una categoría con el mismo nombre
    existing_category = db.query(models.Category).filter(models.Category.name == category_request.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")

    # Crear la nueva categoría
    new_category = crud.create_category(db, category_request.name)

    if not new_category:
        raise HTTPException(status_code=500, detail="Error creating category")

    # Retornar la categoría creada
    return new_category

#Users endpoints

@app.post("/users")
async def create_new_user(user_request: schemas.CreateUserRequest, db: Session = Depends(get_db)):
    # Verificar si ya existe un usuario con el mismo correo
    existing_user = db.query(models.User).filter(models.User.email == user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Crear el nuevo usuario
    new_user = crud.create_user(db, user_request)

    if not new_user:
        raise HTTPException(status_code=500, detail="Error creating user")

    response = "User created successfully"
    # Retornar el usuario creado
    return response

@app.patch("/users/{user_id}")
async def update_user(user_id: int, user_request: schemas.UpdateUserRequest, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    existing_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar los datos del usuario
    updated_user = crud.update_user(db, user_id, user_request)

    if not updated_user:
        raise HTTPException(status_code=500, detail="Error updating user")

    # Retornar el usuario actualizado
    return "User updated successfully"

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    # Obtener todos los usuarios
    users = crud.get_users(db)

    # Retornar los usuarios
    return users

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Obtener el usuario por ID
    user = crud.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retornar el usuario
    return user

@app.get("/users/email/{email}")
async def get_user(email: str, db: Session = Depends(get_db)):
    # Obtener el usuario por correo
    user = crud.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retornar el usuario
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Eliminar el usuario por ID
    deleted_user = crud.delete_user(db, user_id)

    if not deleted_user:
        raise HTTPException(status_code=500, detail="Error deleting user")

    # Retornar mensaje de éxito
    return "User deleted successfully"

#Login endpoint
@app.post("/login-user")
def login( request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Autenticar al usuario
    user = crud.authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Retornar el usuario autenticado
    return user

#Detail endpoints 
@app.get("/details/{product_id}")
def get_details(product_id: int, db: Session = Depends(get_db)):
    try:
        details = crud.get_detail_by_product_id(db, product_id)
        return details
    except Exception as e:
        print(f"Error fetching details: {e}")
        return {"error": "Error fetching details"}
    
@app.post("/details")
def create_detail(detail_request: schemas.CreateDetailProductRequest, db: Session = Depends(get_db)):
    new_detail = crud.create_detail(db, detail_request)
    if not new_detail:
        raise HTTPException(status_code=500, detail="Error creating detail")
    return new_detail

@app.patch("/details/{detail_id}")
def update_detail(detail_id: int, detail_request: schemas.UpdateDetailProductRequest, db: Session = Depends(get_db)):
    existing_detail = db.query(models.ProductDetails).filter(models.ProductDetails.id == detail_id).first()
    if not existing_detail:
        raise HTTPException(status_code=404, detail="Detail not found")
    updated_detail = crud.update_detail(db, detail_id, existing_detail.key, detail_request)
    if not updated_detail:
        raise HTTPException(status_code=500, detail="Error updating detail")
    return updated_detail

@app.delete("/details/{detail_id}")
def delete_detail(detail_id: int, db: Session = Depends(get_db)):
    deleted_detail = crud.delete_detail(db, detail_id)
    if not deleted_detail:
        raise HTTPException(status_code=500, detail="Error deleting detail")
    return "Detail deleted successfully"

#Stock endpoints

@app.get("/stocks/{product_id}")
def get_stock(product_id: int, db: Session = Depends(get_db)):
    try:
        stock = crud.get_stock_by_product_id(db, product_id)
        return stock
    except Exception as e:
        print(f"Error fetching stock: {e}")
        return {"error": "Error fetching stock"}

@app.post("/stocks/{product_id}")
def create_stock(product_id: int, stock_request: schemas.CreateStockRequest, db: Session = Depends(get_db)):
    new_stock = crud.create_stock(db, product_id, stock_request)
    if not new_stock:
        raise HTTPException(status_code=500, detail="Error creating stock")
    return new_stock

@app.patch("/stocks/{stock_id}")
def update_stock(stock_id: int, stock_request: schemas.UpdateStockRequest, db: Session = Depends(get_db)):
    existing_stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not existing_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    updated_stock = crud.update_stock(db, stock_id, stock_request)
    if not updated_stock:
        raise HTTPException(status_code=500, detail="Error updating stock")
    return updated_stock

@app.delete("/stocks/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    deleted_stock = crud.delete_stock(db, stock_id)
    if not deleted_stock:
        raise HTTPException(status_code=500, detail="Error deleting stock")
    return "Stock deleted successfully"

#Orders endpoints

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = crud.get_orders(db)
    return orders

@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders")
def create_order(order_request: schemas.CreateOrderRequest, db: Session = Depends(get_db)):
    new_order = crud.create_order(db, order_request)
    if not new_order:
        raise HTTPException(status_code=500, detail="Error creating order")
    return new_order

@app.patch("/orders/{order_id}")
def update_order(order_id: int, order_request: schemas.UpdateOrderRequest, db: Session = Depends(get_db)):
    existing_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    updated_order = crud.update_order(db, order_id, order_request)
    if not updated_order:
        raise HTTPException(status_code=500, detail="Error updating order")
    return updated_order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    deleted_order = crud.delete_order(db, order_id)
    if not deleted_order:
        raise HTTPException(status_code=500, detail="Error deleting order")
    return "Order deleted successfully"

#OrderDetail endpoints

@app.get("/order-details/{order_id}")
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    order_details = crud.get_order_details_by_order_id(db, order_id)
    return order_details

@app.post("/order-details/{order_id}")
def create_order_detail(order_id: int, order_detail_request: schemas.CreateOrderDetailRequest, db: Session = Depends(get_db)):
    new_order_detail = crud.create_order_detail(db, order_id, order_detail_request)
    if not new_order_detail:
        raise HTTPException(status_code=500, detail="Error creating order detail")
    return new_order_detail

@app.patch("/order-details/{order_detail_id}")
def update_order_detail(order_detail_id: int, order_detail_request: schemas.UpdateOrderDetailRequest, db: Session = Depends(get_db)):
    existing_order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.id == order_detail_id).first()
    if not existing_order_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    updated_order_detail = crud.update_order_detail(db, order_detail_id, order_detail_request)
    if not updated_order_detail:
        raise HTTPException(status_code=500, detail="Error updating order detail")
    return updated_order_detail

@app.delete("/order-details/{order_detail_id}")
def delete_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    deleted_order_detail = crud.delete_order_detail(db, order_detail_id)
    if not deleted_order_detail:
        raise HTTPException(status_code=500, detail="Error deleting order detail")
    return "Order detail deleted successfully"
