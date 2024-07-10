from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud,models,schemas
from .database import SessionLocal, engine
from typing import List


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


@app.get("/products/", response_model=schemas.ProductResponseModel)
def get_products(db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    products = crud.get_products_by_pages(db, page, limit)
    total_amount = crud.get_total_products_count(db)
    product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
    return {
        "page": page,
        "limit": limit,
        "total_amount": total_amount,
        "records": product_models
    }

@app.get("/products_category/{category_id}", response_model=schemas.ProductResponseModel)
def get_products_by_category(db: Session = Depends(get_db), category_id: int=1, page: int=0, limit: int=10):
    products = crud.get_products_by_category(db, category_id, page, limit)
    product_models = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]

    return {
        "page": page,
        "limit": limit,
        "total_amount": len(products),
        "records": product_models
    }

@app.get("/categories/", response_model=List[schemas.CategoryModel])
def get_categories(db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    return categories

@app.get("/products_name/{name}", response_model=schemas.ProductResponseModel)
def get_product_by_name(name: str, db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    products = crud.get_product_by_name(db, name, page, limit)
    products_model = [schemas.ProductModel(id=product.id, name=product.name, price=product.price, discount=product.discount, url_image=product.url_image, category_id=product.category_id) for product in products]
    return {
        "page": page,
        "limit": limit,
        "total_amount": len(products),
        "records": products_model
    }

@app.get("/products_id/{id}", response_model=schemas.ProductModel)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, id)
    return product
