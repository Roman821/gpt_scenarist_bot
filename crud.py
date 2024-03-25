from typing import Type
from abc import ABC

from sqlalchemy.orm import Session

from models import User, HistoryRecord
from database import Base


class BaseCrud(ABC):

    def __init__(self, model: Type[Base], db: Session) -> None:

        self.model = model
        self.db = db

    def add_to_db_and_refresh(self, object_to_add: Type[Base]) -> None:

        self.db.add(object_to_add)
        self.db.commit()
        self.db.refresh(object_to_add)

    def create(self, **kwargs) -> Type[Base]:

        db_object = self.model(**kwargs)

        self.add_to_db_and_refresh(db_object)

        return db_object

    def get(self, **kwargs) -> Type[Base]:
        return self.db.query(self.model).filter_by(**kwargs).first()

    def get_many(self, **kwargs) -> list[Type[Base]]:
        return self.db.query(self.model).filter_by(**kwargs).all()

    def update(self, db_object: Type[Base], **kwargs) -> None:

        for key, value in kwargs.items():
            setattr(db_object, key, value)

        self.db.commit()

    def delete_many(self, **kwargs) -> None:

        self.db.query(self.model).filter_by(**kwargs).delete()

        self.db.commit()


class UserCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(User, db)


class HistoryRecordCrud(BaseCrud):
    def __init__(self, db: Session) -> None:
        super().__init__(HistoryRecord, db)
