from sqlalchemy.orm import Session
from sqlalchemy import text
from utils import models
import time
import requests
from utils import config
from utils import schemas

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

def fetch_root_periodically():
    while True:
        try:
            response = requests.get(config.Settings().url)
            print(response.json())
        except Exception as e:
            print(f"Error fetching root: {e}")
        time.sleep(180)  # Espera 3 minutos

def create_category(db: Session, name: str):
    # Usamos una sentencia SQL para insertar la categoría
    sql_query = text("INSERT INTO category (name) VALUES(:name)")
    db.execute(sql_query, {'name': name})
    db.commit()  # Importante para guardar los cambios en la base de datos
    
    # Recuperar la categoría creada
    new_category = db.execute(text("SELECT * FROM category WHERE name = :name"), {'name': name}).fetchone()
    
    return new_category

def create_product(db: Session, product_request: schemas.CreateProductRequest):
    # Usamos una sentencia SQL para insertar el producto
    sql_query = text("""
        INSERT INTO product (name, price, url_image, category_id, discount)
        VALUES (:name, :price, :url_image, :category_id, :discount)
    """)
    db.execute(sql_query, {
        'name': product_request.name,
        'price': product_request.price,
        'url_image': product_request.url_image,
        'category_id': product_request.category_id,
        'discount': product_request.discount
    })
    db.commit()  # Importante para guardar los cambios en la base de datos
    
    # Recuperar el producto creado
    new_product = db.execute(text("SELECT * FROM product WHERE name = :name"), {'name': product_request.name}).fetchone()
    
    return new_product