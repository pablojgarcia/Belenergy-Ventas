import os, json
os.chdir(os.path.dirname(__file__))
from app.database import SessionLocal
from app import models, schemas
from collections import Counter

db = SessionLocal()
products = db.query(models.Product).filter(
    models.Product.active == True,
    models.Product.sale_ok == True,
).all()

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
    taxes = db.query(models.Tax).filter(models.Tax.odoo_id.in_(tax_ids)).all()
    tax_map = {t.odoo_id: t.name for t in taxes}

result = []
for p in products:
    labels = []
    if p.taxes_id:
        try:
            for tid in json.loads(p.taxes_id):
                labels.append(tax_map.get(tid, f"ID {tid}"))
        except Exception:
            pass
    p.taxes_display = ", ".join(labels) if labels else "Exento"
    out = schemas.ProductOut.model_validate(p)
    d = out.model_dump(exclude={"image"})
    result.append(d)

c = Counter(r["taxes_display"] for r in result)
print("Distribucion de taxes_display:")
for k, v in c.most_common():
    print(f"  {k!r}: {v}")

print(f"\nTotal productos: {len(result)}")
empty = sum(1 for r in result if not r["taxes_display"])
print(f"Con display vacio: {empty}")
db.close()
