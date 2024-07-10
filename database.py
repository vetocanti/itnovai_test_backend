# Description: This file contains the database configuration for the application.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend import config

sqlalchemyDatabseUrl = config.Settings().database_url
engine = create_engine(
    sqlalchemyDatabseUrl
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()