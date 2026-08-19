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

# Matriz de politica_de_descuentos_por_linea.xlsx (monto; por línea de producto).
# Campaña no tiene máximo automático: max_discount=None e is_active=False
# (se reactiva manualmente si hay lógica de campaña).
AMOUNT_RULES = {
    "vendedor_interno": {
        "deye": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0, "campaña": None},
        "huawei": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 15.0, "gt_50000": 15.0, "campaña": None},
        "sungrow": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 20.0, "gt_50000": 30.0, "campaña": None},
        "estructuras": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 20.0, "gt_50000": 30.0, "campaña": None},
        "cables": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0, "campaña": None},
    },
    "representante_general": {
        "deye": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0, "campaña": None},
        "huawei": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 15.0, "gt_50000": 20.0, "campaña": None},
        "sungrow": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 20.0, "gt_50000": 30.0, "campaña": None},
        "estructuras": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 20.0, "gt_50000": 30.0, "campaña": None},
        "cables": {"lt_500": 0.0, "lt_5000": 11.0, "lt_10000": 11.0, "gt_50000": 20.0, "campaña": None},
    },
    "representante_agro": {
        "deye": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0, "campaña": None},
        "huawei": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0, "campaña": None},
        "sungrow": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 30.0, "campaña": None},
        "estructuras": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 30.0, "campaña": None},
        "cables": {"lt_500": 0.0, "lt_5000": 5.0, "lt_10000": 15.0, "gt_50000": 20.0, "campaña": None},
    },
}

# TODO: confirmar con el equipo si la diferencia de Huawei en "USD 50.000+" es intencional:
# Vendedores Internos 15% vs Representantes General 20% (planilla cargada tal cual).
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
        "campaña": (None, None),
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
        # Amount bands (incluye campaña)
        for line_key, amount_bands in AMOUNT_RULES[seller_type].items():
            product_line = db.query(models.ProductLine).filter(
                models.ProductLine.key == line_key
            ).first()
            if not product_line:
                continue

            for band_name, max_disc in amount_bands.items():
                min_val, max_val = BAND_MAP["amount"][band_name]
                is_campaign = band_name == "campaña"
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
                        is_active=not is_campaign,
                        priority=10,
                    ))

        # Qty bands
        for line_key, qty_bands in QTY_RULES[seller_type].items():
            product_line = db.query(models.ProductLine).filter(
                models.ProductLine.key == line_key
            ).first()
            if not product_line:
                continue

            for band_name, max_disc in qty_bands.items():
                min_val, max_val = BAND_MAP["qty"][band_name]
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
                        max_discount=max_disc,
                        requires_approval=False,
                        is_active=True,
                        priority=20,
                    ))

    # Migración idempotente en DBs existentes: tramos sin máximo automático (None).
    # Container (qty >= 720): antes se seedeaba con max_discount=0.0.
    db.query(models.DiscountRule).filter(
        models.DiscountRule.condition_type == "qty",
        models.DiscountRule.min_value == 720.0,
        models.DiscountRule.max_discount != None,
    ).update({models.DiscountRule.max_discount: None})

    # Campaña (amount con min/max nulos): si existiera con valor numérico, se pasa a None.
    db.query(models.DiscountRule).filter(
        models.DiscountRule.condition_type == "amount",
        models.DiscountRule.min_value.is_(None),
        models.DiscountRule.max_value.is_(None),
    ).update({models.DiscountRule.max_discount: None, models.DiscountRule.is_active: False})

    # Prioridades por defecto para reglas creadas antes de la columna priority
    # (solo si quedaron en 0, preservando ajustes manuales).
    db.query(models.DiscountRule).filter(
        models.DiscountRule.condition_type == "amount",
        models.DiscountRule.priority == 0,
    ).update({models.DiscountRule.priority: 10})
    db.query(models.DiscountRule).filter(
        models.DiscountRule.condition_type == "qty",
        models.DiscountRule.priority == 0,
    ).update({models.DiscountRule.priority: 20})

    db.commit()
