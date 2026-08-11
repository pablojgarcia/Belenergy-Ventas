import uuid
import json
import logging
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
from ..integrations.odoo.partner import (
    resolve_app_user_partner_id,
    resolve_res_users_id_by_name,
)
from ..services.customer_creation_service import CustomerCreationService
from ..services.discount_engine import (
    DiscountEngine,
    order_requires_approval,
)
from ..integrations.odoo.industry import (
    user_seller_types,
    auto_industry_for_seller_types,
    effective_seller_type,
)

logger = logging.getLogger(__name__)


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
            raise HTTPException(
                status_code=409,
                detail={"title": "Borrador ya generado", "message": "Este borrador ya fue generado"},
            )

        if draft.status == "failed":
            draft.status = "draft"

        seller_types = user_seller_types(self.user.seller_types)
        has_new_client = draft.customer_id is None and bool(draft.new_client_name)
        industry_name = (
            (draft.new_client_industry or auto_industry_for_seller_types(seller_types))
            if has_new_client else None
        )
        effective_seller_type_name = effective_seller_type(seller_types, industry_name)

        if draft.customer_id is None:
            if draft.new_client_name:
                try:
                    customer = CustomerCreationService(self.db, self.user).create_new_customer(
                        name=draft.new_client_name,
                        vat=draft.new_client_vat,
                        industry_name=industry_name,
                    )
                    draft.customer_id = customer.id
                    draft.new_client_name = None
                    draft.new_client_vat = None
                    self.db.commit()
                except HTTPException:
                    draft.status = "failed"
                    self.db.commit()
                    raise
                except Exception as e:
                    draft.status = "failed"
                    self.db.commit()
                    raise HTTPException(status_code=502, detail=f"Error al crear el cliente nuevo: {e}")
            else:
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
                    detail={
                        "title": "Precio desactualizado",
                        "message": f"El precio del producto '{product.name}' en la línea #{i + 1} cambió. Recargue el borrador.",
                    },
                )

        engine = DiscountEngine(self.db)
        evaluation = engine.evaluate(draft, self.user, seller_type=effective_seller_type_name)

        requires_approval = order_requires_approval(evaluation)
        motivo = (draft.notes or "").strip()
        if requires_approval and not motivo:
            raise HTTPException(
                status_code=400,
                detail={
                    "title": "Solicitud inválida",
                    "message": "La descripción es obligatoria cuando el descuento supera el máximo permitido",
                },
            )

        amount_untaxed = 0.0
        amount_tax = 0.0
        odoo_lines = []
        for i, line in enumerate(lines):
            product = self.product_repo.get_by_id(line.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto ID {line.product_id} no encontrado")

            if product.odoo_id is None:
                raise HTTPException(status_code=400, detail=f"El producto '{product.name}' no tiene un ID válido en Odoo")

            subtotal = line.quantity * line.unit_price * (1 - line.discount / 100)
            amount_untaxed += subtotal
            amount_tax += subtotal * line.tax_rate / 100

            tax_ids = []
            if line.tax_id:
                try:
                    tax_ids = json.loads(line.tax_id)
                except Exception:
                    pass

            eval_result = evaluation[i] if i < len(evaluation) else None

            line.discount_rule_id = eval_result.get("discount_rule_id") if eval_result else None
            line.max_discount_applied = eval_result.get("max_discount") if eval_result else None
            line.seller_type_applied = effective_seller_type_name

            odoo_lines.append({
                "product_id": line.product_odoo_id,
                "quantity": line.quantity,
                "price_unit": line.unit_price,
                "discount": line.discount,
                "tax_ids": tax_ids,
            })

        amount_total = amount_untaxed + amount_tax

        note = draft.notes or ""
        if draft.terms_and_conditions_id:
            terms = self.db.query(models.TermsAndConditions).filter(
                models.TermsAndConditions.id == draft.terms_and_conditions_id,
                models.TermsAndConditions.is_active == True,
            ).first()
            if terms:
                note = terms.content

        try:
            odoo_id = create_quotation(
                partner_id=customer.odoo_id,
                order_lines=odoo_lines,
                description=note,
                user_id=self._resolve_vendedor_interno_id(),
                vendedor_externo_partner_id=self._resolve_vendedor_externo_id(),
                requiere_aprobacion=requires_approval,
                motivo_aprobacion=motivo,
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
            id=draft.id,
            draft_id=draft.id,
            customer_id=draft.customer_id,
            amount_untaxed=amount_untaxed,
            amount_tax=amount_tax,
            amount_total=amount_total,
            odoo_sale_order_id=odoo_id,
            odoo_sale_order_name=odoo_name,
            status="draft",
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

    def _resolve_vendedor_externo_id(self) -> int | None:
        """res.partner que representa al usuario de la app en Odoo (vendedor externo)."""
        vendedor_id = resolve_app_user_partner_id(self.user.email)
        if vendedor_id is None:
            logger.warning(
                "Vendedor externo no resuelto para el usuario '%s' (%s)",
                self.user.username,
                self.user.email,
            )
        return vendedor_id

    def _resolve_vendedor_interno_id(self) -> int | None:
        """res.users (vendedor interno) asignado al usuario de la app."""
        vendedor_id = resolve_res_users_id_by_name(self.user.vendedor_interno)
        if vendedor_id is None:
            logger.warning(
                "Vendedor interno no resuelto para el usuario '%s' (vendedor_interno=%r)",
                self.user.username,
                self.user.vendedor_interno,
            )
        return vendedor_id
