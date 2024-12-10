from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date

#Product
class ProductModel(BaseModel):
    id: int
    name: str
    price: float
    discount: int
    url_image: str
    category_id: int

    class Config:
        from_attributes = True
        
class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    discount: Optional[int] = None
    url_image: Optional[str] = None
    category_id: Optional[int] = None


class ProductResponseModel(BaseModel):
    page: int
    limit: int
    total_amount: int
    records: List[ProductModel]

    class Config:
        from_attributes = True
    
#Category

class CategoryModel(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ErrorResponseModel(BaseModel):
    error: str

class CreateCategoryRequest(BaseModel):
    name: str

class CreateProductRequest(BaseModel): 
    name: str
    price: float
    url_image: Optional[str] = None
    category_id: int
    discount: int
    amount: int
    category_id: int
    
#User
    
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    birthday: date
    is_admin: int

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    is_admin: Optional[bool] = None

#Auth
class LoginRequest(BaseModel):
    email: str
    password: str

#Detail 

class CreateDetailProductRequest(BaseModel):
    product_id: int
    key: str
    value: str

class DetailProductModel(BaseModel):
    id: int
    product_id: int
    key: str
    value: str

    class Config:
        from_attributes = True

class UpdateDetailProductRequest(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    key: Optional[str] = None
    value: Optional[str] = None
    
class CreateStockRequest(BaseModel):
    product_id: int
    quantity: int

class UpdateStockRequest(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None

class StockModel(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True
    
class CreateOrderRequest(BaseModel):
    total: int
    user_id: int   

class OrderModel(BaseModel):
    id: int
    total: int
    user_id: int
    created_at: date

    class Config:
        from_attributes = True

class UpdateOrderRequest(BaseModel):
    id: Optional[int] = None
    total: Optional[int] = None
    user_id: Optional[int] = None
    created_at: Optional[date] = None

class CreateOrderDetailRequest(BaseModel):
    order_id: int
    product_id: int
    quantity: int

class UpdateOrderDetailRequest(BaseModel):
    id: Optional[int] = None
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None

class OrderDetailModel(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


    