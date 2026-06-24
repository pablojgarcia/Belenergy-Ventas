from sqlalchemy.orm import Session
from .. import models


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        return self.db.query(models.User).count()

    def get_by_username(self, username: str) -> models.User | None:
        return self.db.query(models.User).filter(
            models.User.username == username
        ).first()

    def get_by_email(self, email: str) -> models.User | None:
        return self.db.query(models.User).filter(
            models.User.email == email
        ).first()

    def get_by_id(self, user_id: int) -> models.User | None:
        return self.db.query(models.User).filter(
            models.User.id == user_id
        ).first()

    def get_first(self) -> models.User | None:
        return self.db.query(models.User).order_by(models.User.id).first()

    def admin_exists(self) -> bool:
        return self.db.query(models.User).filter(
            models.User.role == "admin"
        ).count() > 0

    def create(self, user: models.User) -> models.User:
        self.db.add(user)
        self.db.flush()
        return user

    def save(self, user: models.User):
        self.db.commit()
