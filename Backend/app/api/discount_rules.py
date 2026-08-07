import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_current_admin
from ..services.discount_engine import DiscountEngine
from ..seed_discount_rules import BAND_MAP
from .. import models, schemas

router = APIRouter(prefix="/discount-rules", tags=["discount-rules"])

BAND_LABELS = {
    "amount": {
        "lt_500": "< 500",
        "lt_5000": "500 – 5.000",
        "lt_10000": "5.000 – 50.000",
        "gt_50000": "> 50.000",
    },
    "qty": {
        "lt_18": "1 – 17 u",
        "medio_pallet": "18 – 35 u (medio pallet)",
        "pallet": "36 – 179 u (pallet)",
        "5_pallets": "180 – 359 u (5 pallets)",
        "10_pallets": "360 – 719 u (10 pallets)",
        "container": "720+ u (container)",
    },
}


@router.post("/evaluate", response_model=list[schemas.DiscountRuleResult])
def evaluate_discount_rules(
    body: schemas.DiscountRuleEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    seller_type = current_user.seller_type or "vendedor_interno"
    lines_data = [
        {"product_id": line.product_id, "quantity": line.quantity, "discount": line.discount}
        for line in body.lines
    ]
    engine = DiscountEngine(db)
    results = engine.evaluate_lines(lines_data, seller_type)
    return [schemas.DiscountRuleResult(**r) for r in results]


@router.get("", response_model=list[schemas.DiscountRuleOut])
def list_discount_rules(
    seller_type: Optional[str] = None,
    product_line_id: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    query = db.query(models.DiscountRule)
    if not include_inactive:
        query = query.filter(models.DiscountRule.is_active == True)
    if seller_type:
        query = query.filter(models.DiscountRule.seller_type == seller_type)
    if product_line_id:
        query = query.filter(
            models.DiscountRule.product_line_id == uuid.UUID(product_line_id)
        )
    return query.order_by(models.DiscountRule.seller_type, models.DiscountRule.created_at).all()


@router.post("", response_model=schemas.DiscountRuleOut)
def create_discount_rule(
    body: schemas.DiscountRuleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    rule = models.DiscountRule(
        seller_type=body.seller_type,
        product_line_id=body.product_line_id,
        condition_type=body.condition_type,
        min_value=body.min_value,
        max_value=body.max_value,
        max_discount=body.max_discount,
        requires_approval=body.requires_approval,
        is_active=True,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/product-lines", response_model=list[schemas.ProductLineOut])
def list_product_lines(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    query = db.query(models.ProductLine)
    if not include_inactive:
        query = query.filter(models.ProductLine.is_active == True)
    return query.order_by(models.ProductLine.key).all()


@router.post("/product-lines", response_model=schemas.ProductLineOut)
def create_product_line(
    body: schemas.ProductLineCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    existing = db.query(models.ProductLine).filter(
        models.ProductLine.key == body.key
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una línea con esa clave")
    line = models.ProductLine(key=body.key, name=body.name, is_active=True)
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@router.put("/product-lines/{line_id}", response_model=schemas.ProductLineOut)
def update_product_line(
    line_id: str,
    body: schemas.ProductLineUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    line = db.query(models.ProductLine).filter(
        models.ProductLine.id == uuid.UUID(line_id)
    ).first()
    if not line:
        raise HTTPException(status_code=404, detail="Línea de producto no encontrada")
    if body.name is not None:
        line.name = body.name
    if body.is_active is not None:
        line.is_active = body.is_active
    db.commit()
    db.refresh(line)
    return line


@router.get("/bands", response_model=list[schemas.DiscountBandOut])
def list_discount_bands(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    bands = []
    for condition_type, bands_map in BAND_MAP.items():
        for band_key, (min_val, max_val) in bands_map.items():
            bands.append(
                {
                    "key": band_key,
                    "label": BAND_LABELS.get(condition_type, {}).get(band_key, band_key),
                    "condition_type": condition_type,
                    "min": min_val,
                    "max": max_val,
                }
            )
    return bands


@router.put("/{rule_id}", response_model=schemas.DiscountRuleOut)
def update_discount_rule(
    rule_id: str,
    body: schemas.DiscountRuleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    rule = db.query(models.DiscountRule).filter(
        models.DiscountRule.id == uuid.UUID(rule_id)
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    fields = body.model_fields_set
    if "seller_type" in fields:
        rule.seller_type = body.seller_type
    if "product_line_id" in fields:
        rule.product_line_id = body.product_line_id
    if "condition_type" in fields:
        rule.condition_type = body.condition_type
    if "min_value" in fields:
        rule.min_value = body.min_value
    if "max_value" in fields:
        rule.max_value = body.max_value
    if "max_discount" in fields:
        rule.max_discount = body.max_discount
    if "requires_approval" in fields:
        rule.requires_approval = body.requires_approval
    if "is_active" in fields:
        rule.is_active = body.is_active

    rule.updated_by = current_user.id
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_discount_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    rule = db.query(models.DiscountRule).filter(
        models.DiscountRule.id == uuid.UUID(rule_id)
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    rule.is_active = False
    rule.updated_by = current_user.id
    db.commit()
    return {"deleted": True}