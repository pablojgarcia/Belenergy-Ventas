from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from ..integrations.odoo import sync_customers, sync_products, sync_taxes
from .. import models

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/customers", status_code=200)
def trigger_sync(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    try:
        sync_customers(db)
        return {"message": "Sincronización completada"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al sincronizar clientes: {str(e)}")


@router.post("/products", status_code=200)
def trigger_sync_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    try:
        sync_taxes(db)
        sync_products(db)
        return {"message": "Sincronización de impuestos y productos completada"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al sincronizar productos: {str(e)}")


@router.post("/taxes", status_code=200)
def trigger_sync_taxes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    try:
        sync_taxes(db)
        return {"message": "Sincronización de impuestos completada"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al sincronizar impuestos: {str(e)}")
