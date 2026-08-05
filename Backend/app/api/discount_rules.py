import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from .. import models, schemas

router = APIRouter(prefix="/discount-rules", tags=["discount-rules"])


@router.get("", response_model=list[schemas.DiscountRuleOut])
def list_discount_rules(
    seller_type: Optional[str] = None,
    product_line_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    query = db.query(models.DiscountRule).filter(
        models.DiscountRule.is_active == True,
    )
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return db.query(models.ProductLine).filter(
        models.ProductLine.is_active == True
    ).order_by(models.ProductLine.key).all()


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

    if body.seller_type is not None:
        rule.seller_type = body.seller_type
    if body.product_line_id is not None:
        rule.product_line_id = body.product_line_id
    if body.condition_type is not None:
        rule.condition_type = body.condition_type
    if body.min_value is not None:
        rule.min_value = body.min_value
    if body.max_value is not None:
        rule.max_value = body.max_value
    if body.max_discount is not None:
        rule.max_discount = body.max_discount
    if body.requires_approval is not None:
        rule.requires_approval = body.requires_approval
    if body.is_active is not None:
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