"""Regresión del caché del motor de descuentos.

El bug: `_get_cached_rules` armaba `rules_by_line` con `rule.product_line_id`
como clave. Desde la base esa clave es `uuid.UUID` (columna `Uuid`), pero desde
Redis llega como `str` (el viaje por json). El lookup de `evaluate_lines` usa
siempre `ProductLine.id`, que es UUID, así que la ruta del caché no matcheaba
nunca: `rules` quedaba vacío y toda línea caía en "no tiene una regla de
descuento aplicable" mientras duraba el TTL.

Estos tests NO pueden omitir el caché: sin `REDIS_URL` la suite nunca entra a la
rama rota y el test pasaría en verde con el bug presente. Por eso se inyecta un
Redis falso y se deja que las reglas pasen por el `json.dumps`/`json.loads` real
de `cache_service`, que es justo donde nace el `str`.
"""

import os
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services import cache_service
from app.services.discount_engine import DiscountEngine


class FakeRedis:
    """Lo mínimo que usan `cache_get` y `cache_set`.

    Guarda el valor tal cual (ya viene serializado por `cache_set`), de modo que
    el round-trip por json ocurre de verdad y no se puede falsear el bug.
    """

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value
        return True

    def delete(self, key):
        self.store.pop(key, None)


def _fresh_db():
    db_path = "test_discount_rule_cache.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine, sessionmaker(bind=engine), db_path


SELLER_TYPE = "representante_general"


class TestDiscountEngineCacheTransparency:
    def setup_method(self):
        self.engine, Session, self.db_path = _fresh_db()
        self.db = Session()

        from app.seed_discount_rules import PRODUCT_LINES, seed_discount_rules

        for pl in PRODUCT_LINES:
            self.db.add(models.ProductLine(key=pl["key"], name=pl["name"], is_active=True))
        self.db.commit()
        seed_discount_rules(self.db)

        self.fake_redis = FakeRedis()
        self._orig_get_redis = cache_service.get_redis
        cache_service.get_redis = lambda: self.fake_redis

    def teardown_method(self):
        cache_service.get_redis = self._orig_get_redis
        self.db.close()
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _seed_panel(self):
        pl = (
            self.db.query(models.ProductLine)
            .filter(models.ProductLine.key == "paneles_astro_575")
            .first()
        )
        product = models.Product(
            name="MODULO BIFACIAL 144 CELDAS. CABLE TIPO N 575W 1,4M ASTRONERGY",
            odoo_id=68,
            default_code="ASTRO-575-BIF",
            list_price=106.375,
            product_line_id=pl.id,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product, pl

    def test_cached_rules_reference_the_same_product_line(self):
        """Invariante estructural: la clave del dict debe ser comparable al id del modelo."""
        product, pl = self._seed_panel()
        engine = DiscountEngine(self.db)
        engine.evaluate_lines(
            [{"product_id": product.id, "quantity": 100, "discount": 0.0}], SELLER_TYPE
        )

        cached = engine._get_cached_rules(SELLER_TYPE, [pl.id])
        assert cached, "no se cachearon reglas: el test no está ejercitando el caché"

        for rule in cached:
            assert isinstance(rule.product_line_id, uuid.UUID), (
                f"product_line_id debería ser UUID, llegó {type(rule.product_line_id)}"
            )
            assert rule.product_line_id == pl.id
            assert isinstance(rule.id, uuid.UUID)

    def test_warm_cache_gives_the_same_result_as_cold_cache(self):
        """El síntoma: la 2da evaluación (desde caché) difiere de la 1ra (desde BD)."""
        product, _ = self._seed_panel()
        engine = DiscountEngine(self.db)
        lines = [{"product_id": product.id, "quantity": 100, "discount": 0.0}]

        cold = engine.evaluate_lines(lines, SELLER_TYPE)[0]
        assert self.fake_redis.store, "la 1ra evaluación debería haber poblado el caché"

        warm = engine.evaluate_lines(lines, SELLER_TYPE)[0]

        assert warm["max_discount"] == cold["max_discount"]
        assert warm["tier"] == cold["tier"]
        assert warm["exceeded"] == cold["exceeded"]
        assert warm["message"] == cold["message"]

    def test_warm_cache_returns_the_actual_discount_not_none(self):
        """100 u de paneles_astro_575 = tramo pallet = 11% (planilla, General)."""
        product, _ = self._seed_panel()
        engine = DiscountEngine(self.db)
        lines = [{"product_id": product.id, "quantity": 100, "discount": 0.0}]

        engine.evaluate_lines(lines, SELLER_TYPE)
        warm = engine.evaluate_lines(lines, SELLER_TYPE)[0]

        assert warm["max_discount"] == 11.0
        assert warm["tier"] == "qty [36–180]"
        assert warm["exceeded"] is False
        assert warm["message"] is None

    def test_amount_band_survives_a_warm_cache(self):
        """El mismo chequeo por una línea con reglas de monto (DEYE)."""
        pl = (
            self.db.query(models.ProductLine)
            .filter(models.ProductLine.key == "deye")
            .first()
        )
        product = models.Product(
            name="Inversor Deye SUN-20K-G05",
            odoo_id=8001,
            default_code="SUN-20K-G05",
            list_price=400.0,
            product_line_id=pl.id,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        engine = DiscountEngine(self.db)
        lines = [{"product_id": product.id, "quantity": 10, "discount": 0.0}]  # 4000 -> <5k

        engine.evaluate_lines(lines, SELLER_TYPE)
        warm = engine.evaluate_lines(lines, SELLER_TYPE)[0]

        assert warm["max_discount"] == 11.0
        assert warm["tier"] == "amount [500–5000]"
        assert warm["message"] is None