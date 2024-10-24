from typing import List
from pydantic import BaseModel

# Pydantic model for Product
class ProductModel(BaseModel):
    id: int
    name: str
    price: float
    discount: int
    url_image: str
    category_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class CategoryModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class ProductResponseModel(BaseModel):
    page: int
    limit: int
    total_amount: int
    records: List[ProductModel]

    class Config:
        orm_mode = True

class ErrorResponseModel(BaseModel):
    error: str

class CreateCategoryRequest(BaseModel):
    name: str

class CreateProductRequest(BaseModel): 
    name: str
    price: float
    url_image: str = None
    category_id: int
    discount: int