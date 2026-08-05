import uuid
from sqlalchemy.orm import Session
from . import models

PRODUCT_LINES = [
    {"key": "deye", "name": "Línea DEYE"},
    {"key": "huawei", "name": "Línea Huawei"},
    {"key": "sungrow", "name": "Línea Sungrow"},
    {"key": "estructuras", "name": "Estructuras"},
    {"key": "cables", "name": "Cables"},
    {"key": "paneles_ja", "name": "Paneles JA"},
    {"key": "paneles_astro_575", "name": "Paneles Astro 575"},
    {"key": "paneles_astro_615", "name": "Paneles Astro 615"},
]

SELLER_TYPES = ["vendedor_interno", "representante_general", "representante_agro"]

AMOUNT_RULES = {
    "vendedor_interno": {
        "deye": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "huawei": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "sungrow": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "estructuras": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "cables": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "paneles_ja": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "paneles_astro_575": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
        "paneles_astro_615": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 15.0},
    },
    "representante_general": {
        "deye": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "huawei": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "sungrow": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "estructuras": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "cables": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "paneles_ja": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "paneles_astro_575": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
        "paneles_astro_615": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0},
    },
    "representante_agro": {
        "deye": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "huawei": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "sungrow": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "estructuras": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "cables": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "paneles_ja": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "paneles_astro_575": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
        "paneles_astro_615": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0},
    },
}

QTY_RULES = {
    "vendedor_interno": {
        "paneles_ja": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_575": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_615": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
    },
    "representante_general": {
        "paneles_ja": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_575": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_615": {"lt_18": 0.0, "medio_pallet": 11.0, "pallet": 11.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
    },
    "representante_agro": {
        "paneles_ja": {"lt_18": 0.0, "medio_pallet": 5.0, "pallet": 15.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_575": {"lt_18": 0.0, "medio_pallet": 5.0, "pallet": 15.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
        "paneles_astro_615": {"lt_18": 0.0, "medio_pallet": 5.0, "pallet": 15.0, "5_pallets": 15.0, "10_pallets": 20.0, "container": None},
    },
}

BAND_MAP = {
    "amount": {
        "lt_500": (0.0, 500.0),
        "lt_5000": (500.0, 5000.0),
        "lt_10000": (5000.0, 50000.0),
        "gt_50000": (50000.0, None),
    },
    "qty": {
        "lt_18": (1.0, 18.0),
        "medio_pallet": (18.0, 36.0),
        "pallet": (36.0, 180.0),
        "5_pallets": (180.0, 360.0),
        "10_pallets": (360.0, 720.0),
        "container": (720.0, None),
    },
}


def seed_product_lines(db: Session):
    for pl in PRODUCT_LINES:
        existing = db.query(models.ProductLine).filter(
            models.ProductLine.key == pl["key"]
        ).first()
        if not existing:
            db.add(models.ProductLine(key=pl["key"], name=pl["name"], is_active=True))
    db.commit()


def seed_discount_rules(db: Session):
    for seller_type in SELLER_TYPES:
        for line_key, amount_bands in AMOUNT_RULES[seller_type].items():
            product_line = db.query(models.ProductLine).filter(
                models.ProductLine.key == line_key
            ).first()
            if not product_line:
                continue

            for band_name, max_disc in amount_bands.items():
                if max_disc is None:
                    continue
                min_val, max_val = BAND_MAP["amount"][band_name]
                existing = db.query(models.DiscountRule).filter(
                    models.DiscountRule.seller_type == seller_type,
                    models.DiscountRule.product_line_id == product_line.id,
                    models.DiscountRule.condition_type == "amount",
                    models.DiscountRule.min_value == min_val,
                    models.DiscountRule.max_value == max_val,
                ).first()
                if not existing:
                    db.add(models.DiscountRule(
                        seller_type=seller_type,
                        product_line_id=product_line.id,
                        condition_type="amount",
                        min_value=min_val,
                        max_value=max_val,
                        max_discount=max_disc,
                        requires_approval=False,
                        is_active=True,
                    ))

        for line_key, qty_bands in QTY_RULES[seller_type].items():
            product_line = db.query(models.ProductLine).filter(
                models.ProductLine.key == line_key
            ).first()
            if not product_line:
                continue

            for band_name, max_disc in qty_bands.items():
                min_val, max_val = BAND_MAP["qty"][band_name]
                requires_approval = band_name == "container"
                existing = db.query(models.DiscountRule).filter(
                    models.DiscountRule.seller_type == seller_type,
                    models.DiscountRule.product_line_id == product_line.id,
                    models.DiscountRule.condition_type == "qty",
                    models.DiscountRule.min_value == min_val,
                    models.DiscountRule.max_value == max_val,
                ).first()
                if not existing:
                    db.add(models.DiscountRule(
                        seller_type=seller_type,
                        product_line_id=product_line.id,
                        condition_type="qty",
                        min_value=min_val,
                        max_value=max_val,
                        max_discount=max_disc if max_disc is not None else 0.0,
                        requires_approval=requires_approval,
                        is_active=True,
                    ))

    db.commit()