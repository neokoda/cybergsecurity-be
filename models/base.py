import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)