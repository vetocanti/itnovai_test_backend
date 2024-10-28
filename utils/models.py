from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from utils import database


class Product(database.Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    price = Column(Float)
    discount = Column(Integer)
    url_image = Column(String(255))
    category_id = Column(Integer, ForeignKey("category.id"), name="category_id")
    category = relationship("Category", back_populates="products")

class Category(database.Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    products = relationship("Product", back_populates="category")