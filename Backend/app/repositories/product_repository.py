from typing import Optional
from sqlalchemy.orm import Session, defer
from .. import models


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> models.Product | None:
        return self.db.query(models.Product).filter(
            models.Product.odoo_id == odoo_id
        ).first()

    def get_by_id(self, product_id: int) -> models.Product | None:
        return self.db.query(models.Product).filter(
            models.Product.id == product_id
        ).first()

    def get_by_ids(self, product_ids: list[int]) -> dict[int, models.Product]:
        if not product_ids:
            return {}
        return {
            p.id: p
            for p in self.db.query(models.Product)
            .filter(models.Product.id.in_(product_ids))
            .all()
        }

    def search(
        self,
        active: bool = True,
        sale_ok: bool = True,
        search: Optional[str] = None,
        categ_id: Optional[str] = None,
    ) -> list[models.Product]:
        # La columna image (LargeBinary) no se usa en el listado y puede
        # pesar MBs: se excluye para no transferirla en cada request.
        q = (
            self.db.query(models.Product)
            .options(defer(models.Product.image))
            .filter(
                models.Product.active == active,
                models.Product.sale_ok == sale_ok,
            )
        )
        if search:
            q = q.filter(models.Product.name.ilike(f"%{search}%"))
        if categ_id:
            q = q.filter(models.Product.categ_id == categ_id)
        return q.all()

    def upsert(self, odoo_id: int, data: dict) -> models.Product:
        product = self.get_by_odoo_id(odoo_id)
        if product:
            for key, value in data.items():
                setattr(product, key, value)
        else:
            product = models.Product(**data)
            self.db.add(product)
        return product
