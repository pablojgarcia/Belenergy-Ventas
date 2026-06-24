import uuid
from typing import Optional
from sqlalchemy.orm import Session
from .. import models


class QuotationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, quotation_id: uuid.UUID) -> models.Quotation | None:
        return self.db.query(models.Quotation).filter(
            models.Quotation.id == quotation_id
        ).first()

    def get_by_draft_id(self, draft_id: uuid.UUID) -> models.Quotation | None:
        return self.db.query(models.Quotation).filter(
            models.Quotation.draft_id == draft_id
        ).first()

    def list(
        self,
        customer_id: Optional[int] = None,
        created_by: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.Quotation]:
        query = self.db.query(models.Quotation)
        if customer_id:
            query = query.filter(models.Quotation.customer_id == customer_id)
        if created_by:
            query = query.filter(models.Quotation.created_by == created_by)
        if date_from:
            query = query.filter(models.Quotation.created_at >= date_from)
        if date_to:
            query = query.filter(models.Quotation.created_at <= date_to)
        return query.order_by(models.Quotation.created_at.desc()).all()

    def create(self, quotation: models.Quotation) -> models.Quotation:
        self.db.add(quotation)
        self.db.flush()
        return quotation

    def save(self):
        self.db.commit()
