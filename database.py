from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

url= os.getenv("database_url")

if not url:
    raise RuntimeError("database url not found")

engine= create_engine(url)

sessionLocal= sessionmaker(
    bind= engine,
    autoflush= False,
    autocommit= False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db= sessionLocal()
    try:
        yield db

    finally:
        db.close()
