from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils import models
import bcrypt
import time
import requests
import jwt
from datetime import datetime, timedelta
from utils import config
from utils import schemas
from services import cloudinary

#CRUD Products

def get_products_by_pages(db: Session, page: int, limit:int):
    if(page<=0):
        page=1
    return db.query(models.Product).offset((page-1)*limit).limit(limit).all()

def get_products_by_category(db: Session, category_id: int, page: int, limit: int):
    if page <= 0:
        page = 1
    return db.query(models.Product).filter(models.Product.category_id == category_id).offset((page-1)*limit).limit(limit)

def get_categories(db: Session):
    return db.query(models.Category).all()

def get_product_by_name(db: Session, name: str, page: int, limit: int):
    offset = page * limit
    query = db.query(models.Product).filter(models.Product.name.like(f'%{name}%')).offset(offset).limit(limit)
    return query.all()

def get_product_by_id(db: Session, id: int):
    return db.query(models.Product).filter(models.Product.id == id).first()

def get_total_products_count(db: Session):
    query = db.query(models.Product).count()
    return query

def get_total_products_count_by_category(db: Session, category_id: int):
    query = db.query(models.Product).filter(models.Product.category_id == category_id).count()
    return query

def get_total_products_count_by_name(db: Session, name: str):
    sql_query = text("SELECT COUNT(*) FROM product WHERE name LIKE :name")
    result = db.execute(sql_query, {'name': f'%{name}%'}).scalar()
    return result

def get_total_products_count_by_price(db: Session, min_price: float, max_price: float, limit: int, page: int):
    offset = page * limit
    sql_query = text("SELECT * FROM product WHERE price >= :min_price AND price <= :max_price LIMIT :limit OFFSET :offset")
    result = db.execute(sql_query, {'min_price': min_price, 'max_price': max_price, 'limit': limit, 'offset': offset}).scalar()
    return result if result is not None else 0

def get_products_with_discount(db: Session, page: int, limit: int):
    offset = page * limit
    query = db.query(models.Product).filter(models.Product.discount > 0).offset(offset).limit(limit)
    return query.all()
def get_products_with_discount_count(db: Session):
    query = db.query(models.Product).filter(models.Product.discount > 0).count()
    return query
def fetch_root_periodically():
    while True:
        try:
            response = requests.get(config.Settings().url)
            print(response.json())
        except Exception as e:
            print(f"Error fetching root: {e}")
        time.sleep(180)  # Espera 3 minutos

def update_product(db: Session, product_id: int, product: schemas.UpdateProductRequest):
    # Verificar si el producto existe
    existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not existing_product:
        raise ValueError("El producto no existe")

    # Actualizar solo los campos proporcionados
    if product.name is not None:
        existing_product.name = product.name
    if product.price is not None:
        existing_product.price = product.price
    if product.discount is not None:
        existing_product.discount = product.discount
    if product.url_image is not None:
        existing_product.url_image = product.url_image
    if product.category_id is not None:
        existing_product.category_id = product.category_id
    if product.amount is not None:
        existing_product.amount = product.amount

    # Guardar cambios
    db.commit()
    db.refresh(existing_product)  # Actualizar el objeto con los valores finales

    return existing_product

def get_product_by_price_range(db: Session, min_price: float, max_price: float, page: int, limit: int):
    offset = page * limit
    # sql query
    price_range_products = db.execute(text("SELECT * FROM product WHERE price >= :min_price AND price <= :max_price LIMIT :limit OFFSET :offset"), {'min_price': min_price, 'max_price': max_price, 'limit': limit, 'offset': offset})
    # SELECT * FROM product WHERE price >= min_price AND price <= max_price LIMIT limit OFFSET offset
    return price_range_products

def delete_product(db: Session, product_id: int):
    # Verificar si el producto existe
    existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not existing_product:
        raise ValueError("El producto no existe")

    # Eliminar los detalles asociados si existen
    for detail in db.query(models.ProductDetails).filter(models.ProductDetails.product_id == product_id).all():
        db.delete(detail)

    # Eliminar el producto
    db.delete(existing_product)
    db.commit()

    return existing_product
        
#CRUD Category

def create_category(db: Session, name: str):
    # Usamos una sentencia SQL para insertar la categoría
    sql_query = text("INSERT INTO category (name) VALUES(:name)")
    db.execute(sql_query, {'name': name})
    db.commit()  # Importante para guardar los cambios en la base de datos
    
    # Recuperar la categoría creada
    new_category = db.execute(text("SELECT * FROM category WHERE name = :name"), {'name': name}).fetchone()
    
    return new_category

def create_product(db: Session, product_request: schemas.CreateProductRequest):
    # Subir la imagen a Cloudinary y obtener la URL
    product_request.url_image = cloudinary.upload_image(product_request.url_image)

    # Crear una instancia del modelo Product
    new_product = models.Product(
        name=product_request.name,
        price=product_request.price,
        url_image=product_request.url_image,
        category_id=product_request.category_id,
        discount=product_request.discount,
        amount=product_request.amount
    )

    # Agregar el nuevo producto a la sesión de la base de datos
    db.add(new_product)
    db.commit()
    db.refresh(new_product)  # Refrescar la instancia para obtener el ID generado

    return new_product
    



# CRUD User 


def create_user(db: Session, user: schemas.CreateUserRequest):
    # Verificar si el correo ya existe
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise ValueError("El correo ya está registrado")

    # Crear instancia del modelo User
    bytes_password = user.password.encode('utf-8')
    hashed = bcrypt.hashpw(bytes_password, bcrypt.gensalt())
    new_user = models.User(
        email=user.email,
        password=hashed,  # Cifrar la contraseña
        first_name=user.first_name,
        last_name=user.last_name,
        birthday=user.birthday,
        is_admin=user.is_admin,
    )

    # Agregar y guardar en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Actualizar el objeto con los valores generados (ID, etc.)

    return new_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: int, user: schemas.UpdateUserRequest):
    # Verificar si el usuario existe
    existing_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not existing_user:
        raise ValueError("El usuario no existe")

    # Actualizar solo los campos proporcionados
    if user.email is not None:
        existing_user.email = user.email
    if user.first_name is not None:
        existing_user.first_name = user.first_name
    if user.last_name is not None:
        existing_user.last_name = user.last_name
    if user.birthday is not None:
        existing_user.birthday = user.birthday
    if user.is_admin is not None:
        existing_user.is_admin = user.is_admin

    # Guardar cambios
    db.commit()
    db.refresh(existing_user)  # Actualizar el objeto con los valores finales

    return existing_user

def delete_user(db: Session, user_id: int):
    # Verificar si el usuario existe
    existing_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not existing_user:
        raise ValueError("El usuario no existe")

    # Eliminar el usuario
    db.delete(existing_user)
    db.commit()

    return existing_user

#JWT

        
def authenticate_user(db: Session, email: str, password: str):
    # Verificar si el usuario existe
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None

    # Verificar la contraseña
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return None

    # Generar un JWT para el usuario
    token_data = {
        "sub": user.email,  # Identificador principal
        "role": user.is_admin,  # Rol del usuario
        "exp": datetime.utcnow() + timedelta(minutes=config.Settings().access_token_expire_minutes),  # Expiración
    }

    token = jwt.encode(token_data, config.Settings().secret_key, algorithm=config.Settings().algorithm)

    # Retornar el token y la información del usuario
    return {
        "access_token": token,
        "token_type": "bearer",
    }

#CRUD Detail Product

def create_detail(db: Session, detail: schemas.CreateDetailProductRequest):
    # Verificar si ya existe un detalle con el mismo product_id y key
    existing_detail = db.query(models.ProductDetails).filter_by(product_id=detail.product_id, key=detail.key).first()
    if existing_detail:
        raise ValueError(f"Detail with product_id {detail.product_id} and key {detail.key} already exists.")
    
    # Crear un nuevo detalle
    new_detail = models.ProductDetails(
        product_id=detail.product_id,
        key=detail.key,
        value=detail.value
    )
    
    db.add(new_detail)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    
    db.refresh(new_detail)
    return new_detail

def get_detail_by_product_id(db: Session, product_id: int):
    return db.query(models.ProductDetails).filter(models.ProductDetails.product_id == product_id).all()

def update_detail(db: Session, id: int, key: str, detail: schemas.CreateDetailProductRequest):
    # Verificar si el detalle existe
    existing_detail = db.query(models.ProductDetails).filter(models.ProductDetails.id == id, models.ProductDetails.key == key).first()
    if not existing_detail:
        raise ValueError("El detalle no existe")

    # Actualizar solo los campos proporcionados
    if detail.value is not None:
        existing_detail.value = detail.value
    
    if detail.key is not None:
        existing_detail.key = detail.key

    # Guardar cambios
    db.commit()
    db.refresh(existing_detail)  # Actualizar el objeto con los valores finales

    return existing_detail

def delete_detail(db: Session, product_id: int, key: str):
    # Verificar si el detalle existe
    existing_detail = db.query(models.ProductDetails).filter(models.ProductDetails.product_id == product_id, models.ProductDetailss.key == key).first()
    if not existing_detail:
        raise ValueError("El detalle no existe")

    # Eliminar el detalle
    db.delete(existing_detail)
    db.commit()

    return existing_detail

#CRUD Stock

def create_stock(db: Session, stock: schemas.CreateStockRequest):
    # Verificar si ya existe un stock con el mismo product_id
    existing_stock = db.query(models.Stock).filter_by(product_id=stock.product_id).first()
    if existing_stock:
        raise ValueError(f"Stock with product_id {stock.product_id} already exists.")
    
    # Crear un nuevo stock
    new_stock = models.Stock(
        product_id=stock.product_id,
        quantity=stock.quantity
    )
    
    db.add(new_stock)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    
    db.refresh(new_stock)
    return new_stock

def get_stock_by_product_id(db: Session, product_id: int):
    return db.query(models.Stock).filter(models.Stock.product_id == product_id).all()

def update_stock(db: Session, product_id: int, stock: schemas.CreateStockRequest):
    # Verificar si el stock existe
    existing_stock = db.query(models.Stock).filter(models.Stock.product_id == product_id).first()
    if not existing_stock:
        raise ValueError("El stock no existe")

    # Actualizar solo los campos proporcionados
    if stock.quantity is not None:
        existing_stock.quantity = stock.quantity

    # Guardar cambios
    db.commit()
    db.refresh(existing_stock)  # Actualizar el objeto con los valores finales

    return existing_stock

def get_stock(db: Session):
    return db.query(models.Stock).all()

def delete_stock(db: Session, product_id: int):
    # Verificar si el stock existe
    existing_stock = db.query(models.Stock).filter(models.Stock.product_id == product_id).first()
    if not existing_stock:
        raise ValueError("El stock no existe")

    # Eliminar el stock
    db.delete(existing_stock)
    db.commit()

    return existing_stock

#CRUD Order

def create_order(db: Session, order: schemas.CreateOrderRequest):
    # Crear una instancia del modelo Order
    new_order = models.Order(
        total=order.total,
        user_id=order.user_id
    )

    # Agregar el nuevo pedido a la sesión de la base de datos
    db.add(new_order)
    db.commit()
    db.refresh(new_order)  # Refrescar la instancia para obtener el ID generado

    return new_order

def get_orders(db: Session):
    return db.query(models.Order).all()

def get_order_by_id(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_order_by_user_id(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def update_order(db: Session, order_id: int, order: schemas.UpdateOrderRequest):
    # Verificar si el pedido existe
    existing_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not existing_order:
        raise ValueError("El pedido no existe")

    # Actualizar solo los campos proporcionados
    if order.total is not None:
        existing_order.total = order.total
    if order.user_id is not None:
        existing_order.user_id = order.user_id

    # Guardar cambios
    db.commit()
    db.refresh(existing_order)  # Actualizar el objeto con los valores finales

    return existing_order

def delete_order(db: Session, order_id: int):
    # Verificar si el pedido existe
    existing_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not existing_order:
        raise ValueError("El pedido no existe")

    # Eliminar el pedido
    db.delete(existing_order)
    db.commit()
    
    return existing_order

#CRUD Detail Order

def create_detail_order(db: Session, detail_order: schemas.CreateOrderDetailRequest):
    # Crear una instancia del modelo DetailOrder
    new_detail_order = models.DetailOrder(
        quantity=detail_order.quantity,
        price=detail_order.price,
        order_id=detail_order.order_id,
        product_id=detail_order.product_id
    )

    # Agregar el nuevo detalle a la sesión de la base de datos
    db.add(new_detail_order)
    db.commit()
    db.refresh(new_detail_order)  # Refrescar la instancia para obtener el ID generado

    return new_detail_order

def get_detail_orders(db: Session):
    return db.query(models.DetailOrder).all()

def get_detail_order_by_id(db: Session, detail_order_id: int):
    return db.query(models.DetailOrder).filter(models.DetailOrder.id == detail_order_id).first()

def get_detail_order_by_order_id(db: Session, order_id: int):
    return db.query(models.DetailOrder).filter(models.DetailOrder.order_id == order_id).all()

def update_detail_order(db: Session, detail_order_id: int, detail_order: schemas.UpdateOrderDetailRequest):
    # Verificar si el detalle existe
    existing_detail_order = db.query(models.DetailOrder).filter(models.DetailOrder.id == detail_order_id).first()
    if not existing_detail_order:
        raise ValueError("El detalle no existe")

    # Actualizar solo los campos proporcionados
    if detail_order.quantity is not None:
        existing_detail_order.quantity = detail_order.quantity
    if detail_order.price is not None:
        existing_detail_order.price = detail_order.price
    if detail_order.order_id is not None:
        existing_detail_order.order_id = detail_order.order_id
    if detail_order.product_id is not None:
        existing_detail_order.product_id = detail_order.product_id

    # Guardar cambios
    db.commit()
    db.refresh(existing_detail_order)  # Actualizar el objeto con los valores finales

    return existing_detail_order

def delete_detail_order(db: Session, detail_order_id: int):
    # Verificar si el detalle existe
    existing_detail_order = db.query(models.DetailOrder).filter(models.DetailOrder.id == detail_order_id).first()
    if not existing_detail_order:
        raise ValueError("El detalle no existe")

    # Eliminar el detalle
    db.delete(existing_detail_order)
    db.commit()

    return existing_detail_order
