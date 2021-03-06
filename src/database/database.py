from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

from ..core.config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_NAME, DATABASE_PASSWORD

engine_postrgesql = create_engine(
    f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')
Session = sessionmaker(bind=engine_postrgesql)
Base = declarative_base(bind=engine_postrgesql)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(engine_postrgesql)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(512))
    group = Column(String(10))
    platform = Column(String(512))
