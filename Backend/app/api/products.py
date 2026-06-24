import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..repositories.product_repository import ProductRepository
from ..repositories.tax_repository import TaxRepository
from .. import models, schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[schemas.ProductOut])
def get_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    search: Optional[str] = Query(None),
    categ_id: Optional[str] = Query(None),
    active: Optional[bool] = Query(True),
    sale_ok: Optional[bool] = Query(True),
):
    product_repo = ProductRepository(db)
    tax_repo = TaxRepository(db)

    products = product_repo.search(active=active, sale_ok=sale_ok, search=search, categ_id=categ_id)

    tax_ids = set()
    for p in products:
        if p.taxes_id:
            try:
                for tid in json.loads(p.taxes_id):
                    tax_ids.add(tid)
            except Exception:
                pass
    tax_map = {}
    if tax_ids:
        taxes = tax_repo.get_by_odoo_ids(list(tax_ids))
        tax_map = {t.odoo_id: {"name": t.name, "amount": t.amount} for t in taxes}

    result = []
    for p in products:
        labels = []
        rate = 0.0
        if p.taxes_id:
            try:
                for tid in json.loads(p.taxes_id):
                    entry = tax_map.get(tid)
                    if entry:
                        labels.append(entry["name"])
                        rate += entry["amount"]
                    else:
                        labels.append(f"ID {tid}")
            except Exception:
                pass
        p.taxes_display = ", ".join(labels) if labels else "Exento"
        p.taxes_rate = rate
        result.append(p)
    return result


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    product = ProductRepository(db).get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("/{product_id}/image")
def get_product_image_endpoint(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    product = ProductRepository(db).get_by_id(product_id)
    if not product or not product.image:
        raise HTTPException(status_code=404, detail="Imagen no disponible")
    return Response(content=product.image, media_type="image/png")
