from sqlalchemy.orm import Session
from .. import models


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> models.Customer | None:
        return self.db.query(models.Customer).filter(
            models.Customer.odoo_id == odoo_id
        ).first()

    def get_by_id(self, customer_id: int) -> models.Customer | None:
        return self.db.query(models.Customer).filter(
            models.Customer.id == customer_id
        ).first()

    def get_by_salesperson(self, salesperson_id: str) -> list[models.Customer]:
        return self.db.query(models.Customer).filter(
            models.Customer.salesperson_id == salesperson_id
        ).all()

    def get_by_salesperson_ids(self, salesperson_ids: list[str]) -> list[models.Customer]:
        return self.db.query(models.Customer).filter(
            models.Customer.salesperson_id.in_(salesperson_ids)
        ).all()

    def get_all(self) -> list[models.Customer]:
        return self.db.query(models.Customer).all()

    def list(
        self,
        salesperson_ids: list[str] | None = None,
        industry: str | None = None,
    ) -> list[models.Customer]:
        query = self.db.query(models.Customer)
        if salesperson_ids:
            query = query.filter(models.Customer.salesperson_id.in_(salesperson_ids))
        if industry:
            query = query.filter(models.Customer.industry == industry)
        return query.all()

    def upsert(self, odoo_id: int, data: dict) -> models.Customer:
        customer = self.get_by_odoo_id(odoo_id)
        if customer:
            for key, value in data.items():
                setattr(customer, key, value)
        else:
            customer = models.Customer(**data)
            self.db.add(customer)
        return customer
