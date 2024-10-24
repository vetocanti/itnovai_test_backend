from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from utils import models,crud,schemas,database
from typing import List
import threading
from fastapi.responses import JSONResponse


models.database.Base.metadata.create_all(bind=database.engine)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
        return JSONResponse(status_code=500, content={"error": "Error fetching products"})

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