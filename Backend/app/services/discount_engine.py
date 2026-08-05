import uuid
from typing import Optional
from sqlalchemy.orm import Session

from .. import models


class DiscountEngine:
    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, draft: models.QuotationDraft, user: models.User) -> list[dict]:
        seller_type = user.seller_type or "vendedor_interno"

        amount_untaxed = 0.0
        for line in draft.lines:
            product = (
                self.db.query(models.Product)
                .filter(models.Product.id == line.product_id)
                .first()
            )
            if product:
                amount_untaxed += line.quantity * product.list_price

        results = []
        for i, line in enumerate(draft.lines):
            product = (
                self.db.query(models.Product)
                .filter(models.Product.id == line.product_id)
                .first()
            )
            if not product:
                results.append(
                    {
                        "line_index": i,
                        "product_name": f"Producto ID {line.product_id}",
                        "product_line_key": None,
                        "max_discount": None,
                        "requires_approval": False,
                        "tier": None,
                        "message": None,
                    }
                )
                continue

            product_line = None
            if product.product_line_id:
                product_line = (
                    self.db.query(models.ProductLine)
                    .filter(models.ProductLine.id == product.product_line_id)
                    .first()
                )

            if not product_line or not product_line.is_active:
                results.append(
                    {
                        "line_index": i,
                        "product_name": product.name or "",
                        "product_line_key": None,
                        "max_discount": None,
                        "requires_approval": False,
                        "tier": None,
                        "message": None,
                    }
                )
                continue

            rules = (
                self.db.query(models.DiscountRule)
                .filter(
                    models.DiscountRule.seller_type == seller_type,
                    models.DiscountRule.product_line_id == product_line.id,
                    models.DiscountRule.is_active == True,
                )
                .all()
            )

            applicable = self._find_applicable_rule(rules, line.quantity, amount_untaxed)

            if applicable is None:
                results.append(
                    {
                        "line_index": i,
                        "product_name": product.name or "",
                        "product_line_key": product_line.key,
                        "max_discount": None,
                        "requires_approval": False,
                        "tier": None,
                        "message": None,
                        "discount_rule_id": None,
                    }
                )
                continue

            max_discount = applicable.max_discount
            requires_approval = applicable.requires_approval
            tier = self._describe_tier(applicable, line.quantity, amount_untaxed)

            if requires_approval:
                message = (
                    f"Este tramo requiere aprobación manual. "
                    f"El descuento automático máximo no aplica."
                )
            elif line.discount > max_discount + 0.001:
                message = (
                    f"El descuento de la línea #{i + 1} ('{product.name}') es "
                    f"{line.discount:.1f}% pero el máximo para este tramo es "
                    f"{max_discount:.1f}%."
                )
            else:
                message = None

            results.append(
                {
                    "line_index": i,
                    "product_name": product.name or "",
                    "product_line_key": product_line.key,
                    "max_discount": max_discount,
                    "requires_approval": requires_approval,
                    "tier": tier,
                    "message": message,
                    "discount_rule_id": applicable.id,
                }
            )

        return results

    def _find_applicable_rule(
        self,
        rules: list[models.DiscountRule],
        quantity: float,
        amount_untaxed: float,
    ) -> Optional[models.DiscountRule]:
        qty_rules = [r for r in rules if r.condition_type == "qty"]
        amount_rules = [r for r in rules if r.condition_type == "amount"]
        kit_rules = [r for r in rules if r.condition_type == "kit"]
        campaign_rules = [r for r in rules if r.condition_type == "campaign"]

        for rule in qty_rules:
            if self._qty_matches(rule, quantity):
                return rule

        for rule in amount_rules:
            if self._amount_matches(rule, amount_untaxed):
                return rule

        for rule in kit_rules:
            return rule

        for rule in campaign_rules:
            return rule

        return None

    def _amount_matches(self, rule: models.DiscountRule, amount: float) -> bool:
        if rule.min_value is not None and amount < rule.min_value:
            return False
        if rule.max_value is not None and amount >= rule.max_value:
            return False
        return True

    def _qty_matches(self, rule: models.DiscountRule, quantity: float) -> bool:
        if rule.min_value is not None and quantity < rule.min_value:
            return False
        if rule.max_value is not None and quantity >= rule.max_value:
            return False
        return True

    def _describe_tier(
        self,
        rule: models.DiscountRule,
        quantity: float,
        amount_untaxed: float,
    ) -> str | None:
        if rule.condition_type == "amount":
            if rule.min_value is not None and rule.max_value is not None:
                return f"amount [{rule.min_value:.0f}–{rule.max_value:.0f}]"
            if rule.min_value is not None:
                return f"amount >= {rule.min_value:.0f}"
        elif rule.condition_type == "qty":
            if rule.min_value is not None and rule.max_value is not None:
                return f"qty [{rule.min_value:.0f}–{rule.max_value:.0f}]"
            if rule.min_value is not None:
                return f"qty >= {rule.min_value:.0f}"
        elif rule.condition_type == "kit":
            return "kit"
        elif rule.condition_type == "campaign":
            return "campaign"
        return None