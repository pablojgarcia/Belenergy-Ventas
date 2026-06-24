import json
import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..repositories.quotation_repository import QuotationRepository


class QuotationQueryService:
    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.user = current_user
        self.quotation_repo = QuotationRepository(db)

    def _enrich(self, quotation: models.Quotation):
        customer = (
            self.db.query(models.Customer)
            .filter(models.Customer.id == quotation.customer_id)
            .first()
        )
        quotation.customer_name = customer.name if customer else None

        lines = (
            self.db.query(models.QuotationDraftLine)
            .filter(models.QuotationDraftLine.draft_id == quotation.draft_id)
            .all()
        )
        for line in lines:
            if isinstance(line.tax_id, str):
                try:
                    line.tax_id = json.loads(line.tax_id)
                except Exception:
                    line.tax_id = []
        self._enrich_line_names(lines)
        quotation.lines = lines
        return quotation

    def _enrich_line_names(self, lines: list[models.QuotationDraftLine]):
        product_ids = list({l.product_id for l in lines if l.product_id})
        if not product_ids:
            return
        products = {
            p.id: p.name
            for p in self.db.query(models.Product)
            .filter(models.Product.id.in_(product_ids))
            .all()
        }
        for line in lines:
            line.product_name = products.get(line.product_id)

    def list(
        self,
        customer_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.Quotation]:
        quotations = self.quotation_repo.list(
            customer_id=customer_id,
            created_by=self.user.id,
            date_from=date_from,
            date_to=date_to,
        )
        customer_ids = list({q.customer_id for q in quotations})
        customers = {
            c.id: c.name
            for c in self.db.query(models.Customer)
            .filter(models.Customer.id.in_(customer_ids))
            .all()
        }
        draft_ids = [q.draft_id for q in quotations]
        all_lines = (
            self.db.query(models.QuotationDraftLine)
            .filter(models.QuotationDraftLine.draft_id.in_(draft_ids))
            .all()
        )
        self._enrich_line_names(all_lines)

        lines_by_draft: dict[uuid.UUID, list[models.QuotationDraftLine]] = {}
        for line in all_lines:
            lines_by_draft.setdefault(line.draft_id, []).append(line)

        for q in quotations:
            q.customer_name = customers.get(q.customer_id)
            lines = lines_by_draft.get(q.draft_id, [])
            for line in lines:
                if isinstance(line.tax_id, str):
                    try:
                        line.tax_id = json.loads(line.tax_id)
                    except Exception:
                        line.tax_id = []
            q.lines = lines
        return quotations

    def get(self, quotation_id: uuid.UUID) -> models.Quotation:
        quotation = self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        return self._enrich(quotation)
