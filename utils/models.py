from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from utils import database
from datetime import datetime


class Product(database.Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    discount = Column(Integer, default=0)
    url_image = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="products")
    details = relationship("ProductDetails", back_populates="product")
    detail_orders = relationship("DetailOrder", back_populates="product")
    stock = relationship("Stock", back_populates="product")
    
class ProductDetails(database.Base):
    __tablename__ = "product_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    product = relationship("Product", back_populates="details")


class Category(database.Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)  # Nombre único y obligatorio

    # Relaciones
    products = relationship("Product", back_populates="category")
    
class Order(database.Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # Clave foránea
    created_at = Column(DateTime, default=datetime.now)

    # Relaciones
    user = relationship("User", back_populates="orders")
    detail_order = relationship("DetailOrder", back_populates="order")


class DetailOrder(database.Base):
    __tablename__ = "detail_order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    order = relationship("Order", back_populates="detail_order")
    product = relationship("Product", back_populates="detail_orders")

class User(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    birthday = Column(Date, nullable=True)
    is_admin = Column(Integer, default=0)

    # Relaciones
    orders = relationship("Order", back_populates="user")
    
class Stock(database.Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    product = relationship("Product", back_populates="stock")