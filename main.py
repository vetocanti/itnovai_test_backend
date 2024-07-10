from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud,models,schemas
from .database import SessionLocal, engine
from typing import List
import threading



models.Base.metadata.create_all(bind=engine)


app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}
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
        return {"error": "Error fetching products"}

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
        return {"error": "Error fetching products"}

@app.get("/categories/", response_model=List[schemas.CategoryModel])
def get_categories(db: Session = Depends(get_db)):
    try:
        categories = crud.get_categories(db)
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return {"error": "Error fetching categories"}

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
        return {"error": "Error fetching products"}

@app.get("/products_id/{id}", response_model=schemas.ProductModel)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        product = crud.get_product_by_id(db, id)
        return product
    except Exception as e:
        print(f"Error fetching product: {e}")
        return {"error": "Error fetching product"}
thread = threading.Thread(target=crud.fetch_root_periodically)
thread.daemon = True
thread.start()