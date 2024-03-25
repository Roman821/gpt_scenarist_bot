from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import set_up_env_var
from get_logger import get_logger


DB_URL = set_up_env_var('DB_URL', get_logger('main').warning)


engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)
