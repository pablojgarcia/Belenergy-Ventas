from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..repositories.customer_repository import CustomerRepository
from ..integrations.odoo.partner import create_partner as odoo_create_partner, check_vat_exists
from ..integrations.odoo.industry import resolve_industry_id
from ..utils.cuit import validar_cuit


class CustomerCreationService:
    """Crea un cliente nuevo en Odoo y lo sincroniza a la base local."""

    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.user = current_user
        self.customer_repo = CustomerRepository(db)

    def create_new_customer(self, name: str, vat: str | None = None, industry_name: str | None = None) -> models.Customer:
        name = (name or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="El nombre del cliente nuevo es obligatorio")

        vat = (vat or "").strip()
        if not vat:
            raise HTTPException(
                status_code=400,
                detail={"title": "Solicitud inválida", "message": "El CUIT es obligatorio para un cliente nuevo"},
            )
        if not validar_cuit(vat):
            raise HTTPException(
                status_code=400,
                detail={"title": "Solicitud inválida", "message": "El CUIT ingresado no es válido"},
            )

        existing = self.db.query(models.Customer).filter(
            models.Customer.cuit == vat
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "title": "Cliente duplicado",
                    "message": f"Ya existe un cliente con ese CUIT: {existing.name}",
                },
            )

        if check_vat_exists(vat):
            raise HTTPException(
                status_code=409,
                detail={
                    "title": "Cliente duplicado",
                    "message": "Ya existe un cliente con ese CUIT en Odoo",
                },
            )

        partner_data = {
            "company_name": name,
            "contact_name": name,
            "vat": vat,
            "vendedor_externo": self.user.email,
        }

        industry_id = resolve_industry_id(industry_name) if industry_name else None
        if industry_id is not None:
            partner_data["industry_id"] = industry_id

        try:
            odoo_partner_id = odoo_create_partner(partner_data)
        except ValueError as e:
            raise HTTPException(
                status_code=409,
                detail={"title": "Error al crear el cliente", "message": str(e)},
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error al crear el cliente en Odoo: {e}")

        local_data = {
            "odoo_id": odoo_partner_id,
            "name": name,
            "company_name": name,
            "vat": vat,
            "cuit": vat,
            "salesperson_id": self.user.email,
            "industry": industry_name,
        }
        customer = self.customer_repo.upsert(odoo_partner_id, local_data)
        self.db.flush()
        return customer
