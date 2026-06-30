import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .. import models


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, lead_id: uuid.UUID) -> models.Lead | None:
        return self.db.query(models.Lead).filter(models.Lead.id == lead_id).first()

    def get_by_user(
        self,
        user_id: int,
        status: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.Lead]:
        query = self.db.query(models.Lead).filter(models.Lead.created_by == user_id)
        return self._apply_filters(query, status, q, date_from, date_to)

    def get_all(
        self,
        status: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.Lead]:
        query = self.db.query(models.Lead)
        return self._apply_filters(query, status, q, date_from, date_to)

    def _apply_filters(self, query, status, q, date_from, date_to):
        if status:
            query = query.filter(models.Lead.status == status)
        if q:
            query = query.filter(
                or_(
                    models.Lead.company_name.ilike(f"%{q}%"),
                    models.Lead.contact_name.ilike(f"%{q}%"),
                    models.Lead.email.ilike(f"%{q}%"),
                )
            )
        if date_from:
            query = query.filter(models.Lead.created_at >= date_from)
        if date_to:
            query = query.filter(models.Lead.created_at <= date_to)
        return query.order_by(models.Lead.created_at.desc()).all()

    def create(self, lead: models.Lead) -> models.Lead:
        self.db.add(lead)
        self.db.flush()
        return lead

    def save(self, lead: models.Lead):
        self.db.commit()

    def delete(self, lead: models.Lead):
        self.db.delete(lead)
        self.db.commit()
