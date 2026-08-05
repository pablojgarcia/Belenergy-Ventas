import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.discount_engine import DiscountEngine


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


def _seed_product(db, name, default_code, list_price, product_line_key):
    pl = db.query(models.ProductLine).filter(models.ProductLine.key == product_line_key).first()
    product = models.Product(
        name=name,
        odoo_id=999001,
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
            seller_type=seller_type,
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
        assert results[0]["max_discount"] == 15.0

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
        assert results[0]["requires_approval"] is True
        assert results[0]["max_discount"] == 0.0

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

    def test_no_product_line_no_validation(self):
        prod = _seed_product(self.db, "Producto sin línea", "SIN-LINEA", 100.0, "deye")
        prod.product_line_id = None
        self.db.commit()
        draft = _seed_draft(self.db, 1, [{"product_id": prod.id, "quantity": 10, "unit_price": 100.0, "discount": 50.0}])
        user = _seed_user(self.db, "test_user_13", "vendedor_interno")
        engine = DiscountEngine(self.db)
        results = engine.evaluate(draft, user)
        assert results[0]["max_discount"] is None
        assert results[0]["message"] is None

    def test_default_seller_type_is_vendedor_interno(self):
        user = _seed_user(self.db, "test_user_14", None)
        assert user.seller_type == "vendedor_interno"

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