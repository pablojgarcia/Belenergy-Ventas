from sqlalchemy.orm import Session
from .. import models


class TaxRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[models.Tax]:
        return self.db.query(models.Tax).all()

    def get_by_odoo_id(self, odoo_id: int) -> models.Tax | None:
        return self.db.query(models.Tax).filter(
            models.Tax.odoo_id == odoo_id
        ).first()

    def get_by_odoo_ids(self, odoo_ids: list[int]) -> list[models.Tax]:
        return self.db.query(models.Tax).filter(
            models.Tax.odoo_id.in_(odoo_ids)
        ).all()

    def upsert(self, odoo_id: int, data: dict) -> models.Tax:
        tax = self.get_by_odoo_id(odoo_id)
        if tax:
            for key, value in data.items():
                setattr(tax, key, value)
        else:
            tax = models.Tax(**data)
            self.db.add(tax)
        return tax
