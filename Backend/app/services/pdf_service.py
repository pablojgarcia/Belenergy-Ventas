import uuid
from fastapi import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import httpx

from .. import config
from ..repositories.quotation_repository import QuotationRepository


class PdfService:
    def __init__(self, db: Session):
        self.db = db
        self.quotation_repo = QuotationRepository(db)

    def download(self, quotation_id: uuid.UUID) -> Response:
        quotation = self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")

        report_name = "sale.report_saleorder"
        pdf_url = (
            f"{config.settings.ODOO_URL}/report/pdf/{report_name}"
            f"/{quotation.odoo_sale_order_id}"
        )

        try:
            with httpx.Client() as client:
                auth_resp = client.post(
                    f"{config.settings.ODOO_URL}/web/session/authenticate",
                    json={
                        "jsonrpc": "2.0",
                        "params": {
                            "db": config.settings.ODOO_DB,
                            "login": config.settings.ODOO_USER,
                            "password": config.settings.ODOO_PASSWORD,
                        },
                    },
                )
                if auth_resp.status_code != 200:
                    raise HTTPException(
                        status_code=502,
                        detail="Error al autenticar en Odoo para descargar el PDF",
                    )

                pdf_resp = client.get(pdf_url)
                if pdf_resp.status_code != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Error al descargar PDF desde Odoo: HTTP {pdf_resp.status_code}",
                    )

                pdf_data = pdf_resp.content
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error al descargar PDF desde Odoo: {e}",
            )

        filename = (
            f"cotizacion_{quotation.odoo_sale_order_name or quotation.odoo_sale_order_id}.pdf"
        )
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
