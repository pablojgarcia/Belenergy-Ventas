from sqlalchemy.orm import Session
from .. import models


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_customer_id(self, customer_id: int) -> list[models.Contact]:
        return self.db.query(models.Contact).filter(
            models.Contact.customer_id == customer_id
        ).all()

    def get_by_customer_ids(self, customer_ids: list[int]) -> list[models.Contact]:
        return self.db.query(models.Contact).filter(
            models.Contact.customer_id.in_(customer_ids)
        ).all()

    def get_by_odoo_id(self, odoo_id: int) -> models.Contact | None:
        return self.db.query(models.Contact).filter(
            models.Contact.odoo_id == odoo_id
        ).first()

    def upsert(self, odoo_id: int, data: dict) -> models.Contact:
        contact = self.get_by_odoo_id(odoo_id)
        if contact:
            for key, value in data.items():
                setattr(contact, key, value)
        else:
            contact = models.Contact(**data)
            self.db.add(contact)
        return contact

    def delete_orphans(self, customer_ids: list[int], keep_odoo_ids: set[int]):
        self.db.query(models.Contact).filter(
            models.Contact.customer_id.in_(customer_ids),
            ~models.Contact.odoo_id.in_(keep_odoo_ids),
        ).delete(synchronize_session=False)
