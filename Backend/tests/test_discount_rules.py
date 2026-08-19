import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.discount_engine import DiscountEngine
from app.integrations.odoo.industry import principal_seller_type


def _fresh_db():
    db_path = "test_discount_engine.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return engine, Session, db_path


def _seed_product_lines(db):
    lines = [
        ("deye", "Línea DEYE"),
        ("huawei", "Línea Huawei"),
        ("sungrow", "Línea Sungrow"),
        ("estructuras", "Estructuras"),
        ("cables", "Cables"),
        ("paneles_ja", "Paneles JA"),
        ("paneles_astro_575", "Paneles Astro 575"),
        ("paneles_astro_615", "Paneles Astro 615"),
    ]
    for key, name in lines:
        existing = db.query(models.ProductLine).filter(models.ProductLine.key == key).first()
        if not existing:
            db.add(models.ProductLine(key=key, name=name, is_active=True))
    db.commit()


def _seed_discount_rules(db):
    from app.seed_discount_rules import seed_discount_rules
    seed_discount_rules(db)


def _seed_product(db, name, default_code, list_price, product_line_key, odoo_id=999001):
    pl = db.query(models.ProductLine).filter(models.ProductLine.key == product_line_key).first()
    product = models.Product(
        name=name,
        odoo_id=odoo_id,
        default_code=default_code,
        list_price=list_price,
        product_line_id=pl.id if pl else None,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def _seed_draft(db, user_id, lines_data):
    draft = models.QuotationDraft(
        customer_id=None,
        new_client_name="Cliente Test",
        new_client_vat="20-12345678-9",
        created_by=user_id,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    for ld in lines_data:
        line = models.QuotationDraftLine(
            draft_id=draft.id,
            product_id=ld["product_id"],
            quantity=ld["quantity"],
            unit_price=ld["unit_price"],
            discount=ld.get("discount", 0.0),
            tax_rate=0.0,
        )
        db.add(line)

    db.commit()
    db.refresh(draft)
    return draft


def _seed_user(db, username, seller_type):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        user = models.User(
            email=f"{username}@test.com",
            username=username,
            name=username.capitalize(),
            role="vendedor",
            hashed_password="dummy",
            seller_types=[seller_type] if seller_type else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


class TestDiscountEngine:
    def setup_method(self):
        self.engine, self.Session, self.db_path = _fresh_db()
        self.db = self.Session()
        _seed_product_lines(self.db)
        _seed_discount_rules(self.db)

    def teardown_method(self):
        self.db.close()
        self.engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_amount_band_lt_500(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-3K-G", "SUN-3K-G", 200.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 2, "unit_price": 200.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_1", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 0.0

    def test_amount_band_lt_5000(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 300.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_2", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 11.0

    def test_amount_band_gte_10000(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-10K-G", "SUN-10K-G", 500.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 25, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_3", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 11.0

    def test_amount_band_gte_50000(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-50K-G", "SUN-50K-G", 2000.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 30, "unit_price": 2000.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_4", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 20.0

    def test_agro_lower_small_amount(self):
        prod = _seed_product(self.db, "Inversor Deye pequeño", "SUN-3K-G", 200.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 200.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_5", "representante_agro")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 5.0

    def test_qty_band_pallet(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 36, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_6", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 11.0

    def test_qty_band_5_pallets(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 180, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_7", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 15.0

    def test_qty_band_10_pallets(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 360, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_8", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 20.0

    def test_qty_band_container_requires_approval(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 720, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_9", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["exceeded"] is True
        assert results[0]["max_discount"] is None

    def test_agro_medio_pallet(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 25, "unit_price": 500.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_10", "representante_agro")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 5.0

    def test_amount_without_discount_is_list_price(self):
        prod = _seed_product(self.db, "Cable 6mm", "CBSOLAM-6MM-PT 100", 50.0, "cables")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 100, "unit_price": 50.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_11", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 11.0

    def test_discount_exceeds_max_returns_violation(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 300.0, "discount": 15.0}])
        user = _seed_user(self.db, "test_user_12", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["message"] is not None
        assert "15.0%" in results[0]["message"]
        assert "11.0%" in results[0]["message"]

    def test_no_product_line_requires_approval(self):
        prod = _seed_product(self.db, "Producto sin línea", "SIN-LINEA", 100.0, "deye")
        prod.product_line_id = None
        self.db.commit()
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 100.0, "discount": 50.0}])
        user = _seed_user(self.db, "test_user_13", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert results[0]["message"] is not None
        assert "no tiene línea de producto asignada" in results[0]["message"]

    def test_default_seller_type_is_vendedor_interno(self):
        user = _seed_user(self.db, "test_user_14", None)
        assert principal_seller_type(user.seller_types) == "vendedor_interno"

    def test_snapshot_has_discount_rule_id(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 300.0, "discount": 10.0}])
        user = _seed_user(self.db, "test_user_15", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 11.0
        assert results[0]["discount_rule_id"] is not None

    def test_no_discount_within_max_allows_generate(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 300.0, "discount": 10.0}])
        user = _seed_user(self.db, "test_user_16", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        violations = [r for r in results if r.get("message")]
        assert len(violations) == 0

    def test_rep_general_higher_discount_than_interno(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-50K-G", "SUN-50K-G", 2000.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 30, "unit_price": 2000.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_17", "representante_general")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 20.0

    def test_representante_agro_gt_50k(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-50K-G", "SUN-50K-G", 2000.0, "deye")
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 30, "unit_price": 2000.0, "discount": 0.0}])
        user = _seed_user(self.db, "test_user_18", "representante_agro")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] == 20.0


class TestDiscountEngineEvaluateLines:
    def setup_method(self):
        self.db_engine, self.Session, self.db_path = _fresh_db()
        self.db = self.Session()
        _seed_product_lines(self.db)
        _seed_discount_rules(self.db)
        self.engine = DiscountEngine(self.db)

    def teardown_method(self):
        self.db.close()
        self.db_engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_amount_band_lt_5000(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 11.0

    def test_amount_4000_vendedor_interno(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 400.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 11.0

    def test_amount_4000_representante_agro(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 400.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] == 5.0

    def test_qty_band_pallet(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 36, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 11.0

    def test_qty_band_container_requires_approval(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 720, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["exceeded"] is True
        assert results[0]["max_discount"] is None

    def test_discount_exceeds_max_returns_violation(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 15.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["message"] is not None
        assert "15.0%" in results[0]["message"]
        assert "11.0%" in results[0]["message"]

    def test_no_product_line_requires_approval(self):
        prod = _seed_product(self.db, "Producto sin línea", "SIN-LINEA", 100.0, "deye")
        prod.product_line_id = None
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 50.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert results[0]["message"] is not None
        assert "no tiene línea de producto asignada" in results[0]["message"]

    def test_inactive_line_requires_approval(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        deye_line = self.db.query(models.ProductLine).filter(models.ProductLine.key == "deye").first()
        deye_line.is_active = False
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert "línea está inactiva" in results[0]["message"]

    def test_active_line_without_match_requires_approval(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 0.5, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert "no tiene una regla de descuento aplicable" in results[0]["message"]

    def test_multiple_lines(self):
        prod1 = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        prod2 = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja", odoo_id=999002)
        lines_data = [
            {"product_id": prod1.id, "quantity": 10, "discount": 0.0},
            {"product_id": prod2.id, "quantity": 36, "discount": 0.0},
        ]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 11.0
        assert results[1]["max_discount"] == 11.0

    def test_panel_qty_outside_bands_no_amount_fallback_requires_approval(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 0.5, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert results[0]["message"] is not None

    def test_qty_rule_on_non_panel_line_within_tramo(self):
        prod = _seed_product(self.db, "Empalme para riel", "EMP-01", 10.0, "estructuras")
        estructuras = self.db.query(models.ProductLine).filter(
            models.ProductLine.key == "estructuras").first()
        self.db.query(models.DiscountRule).filter(
            models.DiscountRule.product_line_id == estructuras.id
        ).update({models.DiscountRule.is_active: False})
        self.db.add(models.DiscountRule(
            seller_type="representante_agro",
            product_line_id=estructuras.id,
            condition_type="qty",
            min_value=1.0,
            max_value=3.0,
            max_discount=90.0,
            requires_approval=False,
            is_active=True,
            priority=20,
        ))
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 2, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] == 90.0
        assert results[0]["exceeded"] is False
        assert results[0]["message"] is None

    def test_qty_rule_on_non_panel_line_over_max(self):
        prod = _seed_product(self.db, "Empalme para riel", "EMP-01", 10.0, "estructuras")
        estructuras = self.db.query(models.ProductLine).filter(
            models.ProductLine.key == "estructuras").first()
        self.db.query(models.DiscountRule).filter(
            models.DiscountRule.product_line_id == estructuras.id
        ).update({models.DiscountRule.is_active: False})
        self.db.add(models.DiscountRule(
            seller_type="representante_agro",
            product_line_id=estructuras.id,
            condition_type="qty",
            min_value=1.0,
            max_value=3.0,
            max_discount=90.0,
            requires_approval=False,
            is_active=True,
            priority=20,
        ))
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 2, "discount": 95.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] == 90.0
        assert results[0]["exceeded"] is True
        assert "90.0%" in results[0]["message"]

    def test_qty_rule_outside_tramo_no_amount_requires_approval(self):
        prod = _seed_product(self.db, "Empalme para riel", "EMP-01", 10.0, "estructuras")
        estructuras = self.db.query(models.ProductLine).filter(
            models.ProductLine.key == "estructuras").first()
        self.db.query(models.DiscountRule).filter(
            models.DiscountRule.product_line_id == estructuras.id
        ).update({models.DiscountRule.is_active: False})
        self.db.add(models.DiscountRule(
            seller_type="representante_agro",
            product_line_id=estructuras.id,
            condition_type="qty",
            min_value=1.0,
            max_value=3.0,
            max_discount=90.0,
            requires_approval=False,
            is_active=True,
            priority=20,
        ))
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 4, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert "no tiene una regla de descuento aplicable" in results[0]["message"]

    def test_higher_priority_qty_wins_over_amount_rule(self):
        prod = _seed_product(self.db, "Empalme para riel", "EMP-01", 10.0, "estructuras")
        estructuras = self.db.query(models.ProductLine).filter(
            models.ProductLine.key == "estructuras").first()
        self.db.query(models.DiscountRule).filter(
            models.DiscountRule.product_line_id == estructuras.id
        ).update({models.DiscountRule.is_active: False})
        self.db.add(models.DiscountRule(
            seller_type="representante_agro",
            product_line_id=estructuras.id,
            condition_type="amount",
            min_value=0.0,
            max_value=None,
            max_discount=5.0,
            requires_approval=False,
            is_active=True,
            priority=10,
        ))
        self.db.add(models.DiscountRule(
            seller_type="representante_agro",
            product_line_id=estructuras.id,
            condition_type="qty",
            min_value=1.0,
            max_value=3.0,
            max_discount=90.0,
            requires_approval=False,
            is_active=True,
            priority=20,
        ))
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 2, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] == 90.0

        lines_data = [{"product_id": prod.id, "quantity": 5, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["max_discount"] == 5.0

    def test_amount_line_ignores_qty_rules(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        deye_line = self.db.query(models.ProductLine).filter(models.ProductLine.key == "deye").first()
        self.db.add(models.DiscountRule(
            seller_type="vendedor_interno",
            product_line_id=deye_line.id,
            condition_type="qty",
            min_value=1.0,
            max_value=18.0,
            max_discount=0.0,
            requires_approval=False,
            is_active=True,
        ))
        self.db.commit()
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 11.0

    def test_amount_line_total_includes_panel_lines(self):
        prod1 = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        prod2 = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja", odoo_id=999002)
        lines_data = [
            {"product_id": prod1.id, "quantity": 10, "discount": 0.0},
            {"product_id": prod2.id, "quantity": 180, "discount": 0.0},
        ]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] == 20.0
        assert results[1]["max_discount"] == 15.0


class TestDiscountEngineExceeded:
    def setup_method(self):
        self.db_engine, self.Session, self.db_path = _fresh_db()
        self.db = self.Session()
        _seed_product_lines(self.db)
        _seed_discount_rules(self.db)
        self.engine = DiscountEngine(self.db)

    def teardown_method(self):
        self.db.close()
        self.db_engine.dispose()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_exceeded_true_when_discount_over_max(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 15.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["exceeded"] is True
        assert results[0]["message"] is not None

    def test_exceeded_false_when_discount_within_max(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 10.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["exceeded"] is False
        assert results[0]["message"] is None

    def test_exceeded_true_34_percent_over_5_percent(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 34.0}]
        results = self.engine.evaluate_lines(lines_data, "representante_agro")
        assert results[0]["exceeded"] is True
        assert "34.0%" in results[0]["message"]

    def test_null_max_discount_always_exceeded_even_with_zero_discount(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 720, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True
        assert results[0]["message"] is not None
        assert "sin descuento máximo automático" in results[0]["message"]

    def test_null_max_discount_exceeded_with_high_discount(self):
        prod = _seed_product(self.db, "Panel JA 615W", "JAM66D45", 500.0, "paneles_ja")
        lines_data = [{"product_id": prod.id, "quantity": 720, "discount": 25.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["max_discount"] is None
        assert results[0]["exceeded"] is True

    def test_inactive_campaign_not_matched(self):
        prod = _seed_product(self.db, "Inversor Deye SUN-5K-G", "SUN-5K-G", 300.0, "deye")
        lines_data = [{"product_id": prod.id, "quantity": 10, "discount": 0.0}]
        results = self.engine.evaluate_lines(lines_data, "vendedor_interno")
        assert results[0]["exceeded"] is False
        assert results[0]["max_discount"] == 11.0


class TestOrderApprovalAggregates:
    def test_order_requires_approval_false_when_none_exceeded(self):
        from app.services.discount_engine import order_motivo_aprobacion, order_requires_approval
        lines = [
            {"line_index": 0, "exceeded": False, "message": None},
            {"line_index": 1, "exceeded": False, "message": None},
        ]
        assert order_requires_approval(lines) is False
        assert order_motivo_aprobacion(lines) == ""

    def test_order_requires_approval_true_when_any_exceeded(self):
        from app.services.discount_engine import order_requires_approval
        lines = [
            {"line_index": 0, "exceeded": False, "message": None},
            {"line_index": 1, "exceeded": True, "message": "descuento excedido"},
        ]
        assert order_requires_approval(lines) is True

    def test_order_motivo_aprobacion_joins_multiple_lines(self):
        from app.services.discount_engine import order_motivo_aprobacion
        lines = [
            {"line_index": 0, "exceeded": True, "message": "Línea 1 excede"},
            {"line_index": 1, "exceeded": True, "message": "Línea 2 excede"},
            {"line_index": 2, "exceeded": False, "message": None},
        ]
        motivo = order_motivo_aprobacion(lines)
        assert "Línea 1 excede" in motivo
        assert "Línea 2 excede" in motivo

    def test_order_requires_approval_defensive_empty(self):
        from app.services.discount_engine import order_motivo_aprobacion, order_requires_approval
        assert order_requires_approval([]) is False
        assert order_motivo_aprobacion([]) == ""