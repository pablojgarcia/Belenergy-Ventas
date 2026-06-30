import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .. import models
from ..repositories.lead_repository import LeadRepository
from ..repositories.customer_repository import CustomerRepository
from ..services.draft_service import DraftService
from ..integrations.odoo.crm_lead import create_crm_lead, check_cuit_exists, check_crm_lead_status
from ..integrations.odoo.partner import create_partner as odoo_create_partner


class LeadService:
    def __init__(self, db: Session, current_user: models.User):
        self.db = db
        self.user = current_user
        self.repo = LeadRepository(db)

    def _get_or_404(self, lead_id: uuid.UUID) -> models.Lead:
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        return lead

    def _check_ownership(self, lead: models.Lead):
        if self.user.role != "admin" and lead.created_by != self.user.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a este lead",
            )

    def create(self, data: dict) -> models.Lead:
        lead = models.Lead(
            company_name=data["company_name"],
            contact_name=data.get("contact_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            mobile=data.get("mobile"),
            street=data.get("street"),
            city=data.get("city"),
            state=data.get("state"),
            zip=data.get("zip"),
            country=data.get("country"),
            vat=data.get("vat"),
            notes=data.get("notes"),
            created_by=self.user.id,
        )
        self.repo.create(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get(self, lead_id: uuid.UUID) -> models.Lead:
        lead = self._get_or_404(lead_id)
        self._check_ownership(lead)
        return lead

    def list(
        self,
        status: Optional[str] = None,
        q: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[models.Lead]:
        if self.user.role == "admin":
            return self.repo.get_all(
                status=status, q=q, date_from=date_from, date_to=date_to
            )
        return self.repo.get_by_user(
            user_id=self.user.id,
            status=status,
            q=q,
            date_from=date_from,
            date_to=date_to,
        )

    def update(self, lead_id: uuid.UUID, data: dict) -> models.Lead:
        lead = self._get_or_404(lead_id)
        self._check_ownership(lead)

        if lead.status != "pendiente":
            raise HTTPException(
                status_code=409,
                detail="Solo se puede modificar un lead en estado pendiente",
            )

        if lead.version != data.get("version"):
            raise HTTPException(
                status_code=409,
                detail="El lead fue modificado por otro usuario. Recargue e intente nuevamente.",
            )

        for field in ["company_name", "contact_name", "email", "phone", "mobile",
                       "street", "city", "state", "zip", "country", "vat", "notes"]:
            if field in data and data[field] is not None:
                setattr(lead, field, data[field])

        lead.version += 1
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def delete(self, lead_id: uuid.UUID):
        lead = self._get_or_404(lead_id)
        self._check_ownership(lead)

        if lead.status != "pendiente":
            raise HTTPException(
                status_code=409,
                detail="Solo se pueden eliminar leads en estado pendiente",
            )

        self.repo.delete(lead)

    def approve(self, lead_id: uuid.UUID) -> models.Lead:
        lead = self._get_or_404(lead_id)

        if lead.status != "pendiente":
            raise HTTPException(
                status_code=409,
                detail="El lead ya fue revisado",
            )

        lead.status = "aprobado"
        lead.reviewed_by = self.user.id
        lead.reviewed_at = func.now()
        self.db.commit()

        try:
            self._sync_to_odoo(lead)
        except Exception:
            pass

        self.db.refresh(lead)
        return lead

    def reject(self, lead_id: uuid.UUID, rejection_reason: str) -> models.Lead:
        lead = self._get_or_404(lead_id)

        if lead.status != "pendiente":
            raise HTTPException(
                status_code=409,
                detail="El lead ya fue revisado",
            )

        lead.status = "rechazado"
        lead.rejection_reason = rejection_reason
        lead.reviewed_by = self.user.id
        lead.reviewed_at = func.now()
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def sync(self, lead_id: uuid.UUID) -> models.Lead:
        lead = self._get_or_404(lead_id)

        if lead.status == "sincronizado":
            raise HTTPException(
                status_code=409,
                detail="El lead ya fue sincronizado a Odoo",
            )

        if lead.status == "rechazado":
            raise HTTPException(
                status_code=409,
                detail="No se puede sincronizar un lead rechazado",
            )

        self._sync_to_odoo(lead)
        self.db.refresh(lead)
        return lead

    def _sync_to_odoo(self, lead: models.Lead):
        try:
            cuit = lead.vat
            if cuit:
                existing = self.db.query(models.Customer).filter(
                    models.Customer.cuit == cuit
                ).first()
                if existing:
                    lead.status = "rechazado"
                    lead.rejection_reason = "Ya existe un cliente con ese CUIT"
                    self.db.commit()
                    raise HTTPException(
                        status_code=409,
                        detail="Ya existe un cliente con ese CUIT",
                    )

                if check_cuit_exists(cuit):
                    lead.status = "rechazado"
                    lead.rejection_reason = "Ya existe un cliente con ese CUIT en Odoo"
                    self.db.commit()
                    raise HTTPException(
                        status_code=409,
                        detail="Ya existe un cliente con ese CUIT en Odoo",
                    )

            vendedor_email = self.db.query(models.User).filter(
                models.User.id == lead.created_by
            ).first()

            crm_data = {
                "company_name": lead.company_name,
                "contact_name": lead.contact_name,
                "email": lead.email,
                "phone": lead.phone,
                "mobile": lead.mobile,
                "street": lead.street,
                "city": lead.city,
                "state": lead.state,
                "zip": lead.zip,
                "country": lead.country,
                "vat": lead.vat,
                "notes": lead.notes,
                "vendedor_externo": vendedor_email.email if vendedor_email else None,
            }

            crm_lead_id = create_crm_lead(crm_data)
            lead.odoo_crm_lead_id = crm_lead_id
            lead.status = "sincronizado"
            self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=502,
                detail=f"Error al crear el lead en Odoo: {str(e)}",
            )

    def refresh(self, lead_id: uuid.UUID) -> models.Lead:
        lead = self._get_or_404(lead_id)
        if not lead.odoo_crm_lead_id:
            raise HTTPException(
                status_code=400,
                detail="El lead no ha sido sincronizado a Odoo",
            )

        odoo_status = check_crm_lead_status(lead.odoo_crm_lead_id)

        if odoo_status.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail="Lead no encontrado en Odoo",
            )

        if odoo_status.get("status") == "error":
            raise HTTPException(
                status_code=502,
                detail=f"Error al consultar Odoo: {odoo_status.get('detail')}",
            )

        if not odoo_status.get("active", True):
            lead.status = "rechazado"
            lead.rejection_reason = "Rechazado en Odoo CRM"
        elif odoo_status.get("is_won"):
            lead.status = "aprobado"
        else:
            lead.status = "sincronizado"

        self.db.commit()
        self.db.refresh(lead)
        return lead

    def create_partner(self, lead_id: uuid.UUID) -> dict:
        lead = self._get_or_404(lead_id)

        if lead.status != "aprobado":
            raise HTTPException(
                status_code=409,
                detail="Solo se puede crear un cliente para leads aprobados",
            )

        if lead.odoo_partner_id:
            customer = CustomerRepository(self.db).get_by_odoo_id(lead.odoo_partner_id)
            return {
                "odoo_partner_id": lead.odoo_partner_id,
                "customer_id": customer.id if customer else None,
            }

        if not lead.odoo_crm_lead_id:
            raise HTTPException(
                status_code=409,
                detail="El lead debe estar sincronizado a Odoo primero",
            )

        partner_data = {
            "company_name": lead.company_name,
            "contact_name": lead.contact_name,
            "email": lead.email,
            "phone": lead.phone,
            "mobile": lead.mobile,
            "street": lead.street,
            "city": lead.city,
            "state": lead.state,
            "zip": lead.zip,
            "country": lead.country,
            "vat": lead.vat,
        }

        vendedor = self.db.query(models.User).filter(
            models.User.id == lead.created_by
        ).first()
        if vendedor:
            partner_data["vendedor_externo"] = vendedor.email

        try:
            odoo_partner_id = odoo_create_partner(partner_data)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error al crear el cliente en Odoo: {str(e)}",
            )

        vendedor_email = vendedor.email if vendedor else ""

        local_data = {
            "odoo_id": odoo_partner_id,
            "name": lead.company_name or lead.contact_name or "Sin nombre",
            "company_name": lead.company_name or "",
            "email": lead.email or "",
            "phone": lead.phone or "",
            "mobile": lead.mobile or "",
            "street": lead.street or "",
            "city": lead.city or "",
            "state": lead.state or "",
            "zip": lead.zip or "",
            "country": lead.country or "",
            "vat": lead.vat or "",
            "cuit": lead.vat or "",
            "salesperson_id": vendedor_email,
        }
        local_customer = CustomerRepository(self.db).upsert(odoo_partner_id, local_data)
        self.db.flush()

        lead.odoo_partner_id = odoo_partner_id
        self.db.commit()
        self.db.refresh(lead)
        return {
            "odoo_partner_id": odoo_partner_id,
            "customer_id": local_customer.id,
        }

    def create_quotation_draft(self, lead_id: uuid.UUID) -> dict:
        partner_result = self.create_partner(lead_id)
        customer_id = partner_result.get("customer_id")
        odoo_partner_id = partner_result.get("odoo_partner_id")

        if not customer_id:
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener el ID del cliente local",
            )

        return {
            "customer_id": customer_id,
            "odoo_partner_id": odoo_partner_id,
        }
