import uuid
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..repositories.draft_repository import DraftRepository
from ..repositories.draft_line_repository import DraftLineRepository
from ..repositories.quotation_repository import QuotationRepository
from ..repositories.customer_repository import CustomerRepository
from ..repositories.product_repository import ProductRepository
from ..integrations.odoo.sale import create_quotation
from ..integrations.odoo.client import get_odoo_connection


class QuotationGenerationService:
    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.user = current_user
        self.draft_repo = DraftRepository(db)
        self.line_repo = DraftLineRepository(db)
        self.quotation_repo = QuotationRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.product_repo = ProductRepository(db)

    def generate(self, draft_id: uuid.UUID) -> dict:
        draft = self.draft_repo.get_by_id(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Borrador no encontrado")

        if draft.status == "generated":
            raise HTTPException(status_code=409, detail="Este borrador ya fue generado")

        if draft.status == "failed":
            draft.status = "draft"

        if draft.customer_id is None:
            raise HTTPException(status_code=400, detail="El borrador debe tener un cliente asignado")

        customer = self.customer_repo.get_by_id(draft.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        if customer.odoo_id is None:
            raise HTTPException(status_code=400, detail="El cliente no tiene un ID válido en Odoo")

        if not draft.lines:
            raise HTTPException(status_code=400, detail="El borrador debe tener al menos una línea")

        lines = draft.lines
        for i, line in enumerate(lines):
            if line.quantity <= 0:
                raise HTTPException(status_code=400, detail=f"La línea #{i + 1} debe tener cantidad mayor a cero")

            product = self.product_repo.get_by_id(line.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto ID {line.product_id} no encontrado")

            if product.odoo_id is None:
                raise HTTPException(status_code=400, detail=f"El producto '{product.name}' no tiene un ID válido en Odoo")

            if abs(line.unit_price - product.list_price) > 0.001:
                raise HTTPException(
                    status_code=409,
                    detail=f"El precio del producto '{product.name}' en la línea #{i + 1} cambió. Recargue el borrador.",
                )

        amount_untaxed = 0.0
        amount_tax = 0.0
        odoo_lines = []
        for line in lines:
            subtotal = line.quantity * line.unit_price * (1 - line.discount / 100)
            amount_untaxed += subtotal
            amount_tax += subtotal * line.tax_rate / 100

            tax_ids = []
            if line.tax_id:
                try:
                    tax_ids = json.loads(line.tax_id)
                except Exception:
                    pass

            odoo_lines.append({
                "product_id": line.product_odoo_id,
                "quantity": line.quantity,
                "price_unit": line.unit_price,
                "discount": line.discount,
                "tax_ids": tax_ids,
            })

        amount_total = amount_untaxed + amount_tax

        try:
            odoo_id = create_quotation(
                partner_id=customer.odoo_id,
                order_lines=odoo_lines,
                description=draft.notes or "",
                vendedor_externo=customer.salesperson_id,
            )
        except ValueError as e:
            draft.status = "failed"
            self.db.commit()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            draft.status = "failed"
            self.db.commit()
            raise HTTPException(status_code=502, detail=f"Error al comunicarse con Odoo: {e}")

        odoo_name = None
        try:
            odoo = get_odoo_connection()
            sale = odoo.env["sale.order"].read(odoo_id, ["name"])
            if sale:
                odoo_name = sale[0].get("name")
        except Exception:
            pass

        quotation = models.Quotation(
            draft_id=draft.id,
            customer_id=draft.customer_id,
            amount_untaxed=amount_untaxed,
            amount_tax=amount_tax,
            amount_total=amount_total,
            odoo_sale_order_id=odoo_id,
            odoo_sale_order_name=odoo_name,
            created_by=self.user.id,
        )
        self.quotation_repo.create(quotation)

        draft.status = "generated"
        draft.updated_by = self.user.id
        self.db.commit()

        return {
            "quotation_id": str(quotation.id),
            "odoo_sale_order_id": odoo_id,
            "odoo_sale_order_name": odoo_name,
        }
