from sqlalchemy.orm import Session
from sqlalchemy import text
from utils import models
import time
import requests
from utils import config

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