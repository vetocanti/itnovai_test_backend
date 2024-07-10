from sqlalchemy.orm import Session
from . import models
import time
import requests

def get_products_by_pages(db: Session, page: int, limit:int):
    if(page<=0):
        page=1
    return db.query(models.Product).offset((page-1)*limit).limit(limit).all()

def get_products_by_category(db: Session, category_id: int, page: int, limit: int):
    if page <= 0:
        page = 1
    return db.query(models.Product).filter(models.Product.category_id == category_id).offset((page-1)*limit).limit(limit).all()

def get_categories(db: Session):
    return db.query(models.Category).all()

def get_product_by_name(db: Session, name: str, page: int, limit:int):
    if(page<=0):
        page=1
    return db.query(models.Product).filter(models.Product.name.contains(name)).offset((page-1)*limit).limit(limit).all()

def get_product_by_id(db: Session, id: int):
    return db.query(models.Product).filter(models.Product.id == id).first()

def get_total_products_count(db: Session):
    return db.query(models.Product).count()

def fetch_root_periodically():
    while True:
        try:
            response = requests.get("http://localhost:8000/")
            print(response.json())
        except Exception as e:
            print(f"Error fetching root: {e}")
        time.sleep(180)  # Espera 3 minutos