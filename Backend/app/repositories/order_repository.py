from typing import Optional
from sqlalchemy.orm import Session
from .. import models


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: int) -> models.Order | None:
        return self.db.query(models.Order).filter(
            models.Order.id == order_id
        ).first()

    def get_by_user_id(self, user_id: int, state: Optional[str] = None) -> list[models.Order]:
        q = self.db.query(models.Order).filter(models.Order.user_id == user_id)
        if state:
            q = q.filter(models.Order.state == state)
        return q.all()

    def create(self, order: models.Order) -> models.Order:
        self.db.add(order)
        self.db.flush()
        return order

    def save(self, order: models.Order):
        self.db.commit()


class OrderLineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(self, order_id: int) -> list[models.OrderLine]:
        return self.db.query(models.OrderLine).filter(
            models.OrderLine.order_id == order_id
        ).order_by(models.OrderLine.id).all()

    def count_by_order_id(self, order_id: int) -> int:
        return self.db.query(models.OrderLine).filter(
            models.OrderLine.order_id == order_id
        ).count()

    def create(self, line: models.OrderLine) -> models.OrderLine:
        self.db.add(line)
        return line


class OrderStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(self, order_id: int) -> list[models.OrderStatus]:
        return self.db.query(models.OrderStatus).filter(
            models.OrderStatus.order_id == order_id
        ).order_by(models.OrderStatus.changed_at.desc()).all()

    def get_last(self, order_id: int) -> models.OrderStatus | None:
        return self.db.query(models.OrderStatus).filter(
            models.OrderStatus.order_id == order_id
        ).order_by(models.OrderStatus.changed_at.desc()).first()

    def create(self, status: models.OrderStatus) -> models.OrderStatus:
        self.db.add(status)
        return status


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_jti(self, jti: str) -> models.RefreshToken | None:
        return self.db.query(models.RefreshToken).filter(
            models.RefreshToken.jti == jti
        ).first()

    def create(self, token: models.RefreshToken) -> models.RefreshToken:
        self.db.add(token)
        return token
