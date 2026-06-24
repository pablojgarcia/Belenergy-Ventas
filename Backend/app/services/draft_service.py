import uuid
import json
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..repositories.draft_repository import DraftRepository
from ..repositories.draft_line_repository import DraftLineRepository
from ..repositories.customer_repository import CustomerRepository
from ..repositories.product_repository import ProductRepository
from ..repositories.tax_repository import TaxRepository


class DraftService:
    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.user = current_user
        self.draft_repo = DraftRepository(db)
        self.line_repo = DraftLineRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.product_repo = ProductRepository(db)
        self.tax_repo = TaxRepository(db)

    def create(self, customer_id: Optional[int] = None, notes: Optional[str] = None, lines_data: Optional[list] = None) -> models.QuotationDraft:
        if customer_id:
            customer = self.customer_repo.get_by_id(customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")

        draft = models.QuotationDraft(
            customer_id=customer_id,
            notes=notes,
            created_by=self.user.id,
        )
        self.draft_repo.create(draft)

        if lines_data:
            for line_data in lines_data:
                product = self.product_repo.get_by_id(line_data.get("product_id"))
                product_odoo_id = product.odoo_id if product else None
                tax_rate = 0.0
                if line_data.get("tax_id"):
                    taxes = self.tax_repo.get_by_odoo_ids(line_data["tax_id"])
                    tax_rate = sum(t.amount for t in taxes)
                line = models.QuotationDraftLine(
                    draft_id=draft.id,
                    product_id=line_data["product_id"],
                    product_odoo_id=product_odoo_id,
                    quantity=line_data["quantity"],
                    unit_price=line_data["unit_price"],
                    discount=line_data.get("discount", 0.0),
                    tax_id=json.dumps(line_data.get("tax_id", [])),
                    tax_rate=tax_rate,
                )
                self.line_repo.create(line)

        self.db.commit()
        self.db.refresh(draft)
        self._enrich_lines(draft)
        return draft

    def _enrich_lines(self, draft: models.QuotationDraft):
        product_ids = list({line.product_id for line in draft.lines if line.product_id})
        products = {
            p.id: p.name
            for p in self.db.query(models.Product)
            .filter(models.Product.id.in_(product_ids))
            .all()
        }
        for line in draft.lines:
            line.product_name = products.get(line.product_id)
        return draft

    def _enrich(self, draft: models.QuotationDraft):
        if draft.customer_id:
            customer = (
                self.db.query(models.Customer)
                .filter(models.Customer.id == draft.customer_id)
                .first()
            )
            draft.customer_name = customer.name if customer else None
        self._enrich_lines(draft)
        return draft

    def get(self, draft_id: uuid.UUID) -> models.QuotationDraft:
        draft = self.draft_repo.get_by_id(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Borrador no encontrado")
        return self._enrich(draft)

    def list(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.QuotationDraft]:
        drafts = self.draft_repo.list(
            customer_id=customer_id,
            status=status,
            created_by=self.user.id,
            q=q,
            date_from=date_from,
            date_to=date_to,
        )
        customer_ids = list({d.customer_id for d in drafts if d.customer_id})
        customers = {
            c.id: c.name
            for c in self.db.query(models.Customer)
            .filter(models.Customer.id.in_(customer_ids))
            .all()
        }
        for d in drafts:
            d.customer_name = customers.get(d.customer_id)
            self._enrich_lines(d)
        return drafts

    def update(
        self,
        draft_id: uuid.UUID,
        customer_id: Optional[int],
        notes: Optional[str],
        lines_data: List[dict],
        version: int,
    ) -> models.QuotationDraft:
        draft = self.draft_repo.get_by_id(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Borrador no encontrado")

        if draft.status != "draft":
            raise HTTPException(status_code=409, detail="No se puede modificar un borrador que ya fue generado")

        if draft.version != version:
            raise HTTPException(
                status_code=409,
                detail="El borrador fue modificado por otro usuario. Recargue e intente nuevamente.",
            )

        if customer_id is not None:
            customer = self.customer_repo.get_by_id(customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")

        draft.customer_id = customer_id
        draft.notes = notes
        draft.updated_by = self.user.id
        draft.version += 1

        self.line_repo.delete_by_draft_id(draft_id)
        for line_data in lines_data:
            product = self.product_repo.get_by_id(line_data["product_id"])
            product_odoo_id = product.odoo_id if product else None

            tax_rate = 0.0
            if line_data.get("tax_id"):
                taxes = self.tax_repo.get_by_odoo_ids(line_data["tax_id"])
                tax_rate = sum(t.amount for t in taxes)

            line = models.QuotationDraftLine(
                draft_id=draft_id,
                product_id=line_data["product_id"],
                product_odoo_id=product_odoo_id,
                quantity=line_data["quantity"],
                unit_price=line_data["unit_price"],
                discount=line_data.get("discount", 0.0),
                tax_id=json.dumps(line_data.get("tax_id", [])),
                tax_rate=tax_rate,
            )
            self.line_repo.create(line)

        self.db.commit()
        self.db.refresh(draft)
        return self.draft_repo.get_by_id(draft_id)

    def delete(self, draft_id: uuid.UUID):
        draft = self.draft_repo.get_by_id(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Borrador no encontrado")
        if draft.status != "draft":
            raise HTTPException(status_code=409, detail="Solo se pueden eliminar borradores en estado draft")
        self.draft_repo.delete(draft)
        self.db.commit()
