"""fix: usuarios con seller_type legacy vendedor_interno

El commit 477a88e (2026-08-19) elimino el seller_type `vendedor_interno` de la
matriz de descuentos, dejo las tres funciones de `industry.py` con
`DEFAULT_SELLER_TYPE` como fallback, y borro las reglas con b4c5d6e7f8a9.

Lo que no hizo fue migrar los datos: quedan usuarios con
`seller_types = ["vendedor_interno"]` explicito. El fallback solo dispara cuando
la lista viene vacia, asi que esos usuarios resuelven a un seller_type sin
reglas y TODAS sus lineas caen en "no tiene una regla de descuento aplicable,
requiere aprobacion manual".

- `admin` pasa a `["representante_general", "representante_agro"]`, igual que
  `pablo` y `bruno` (los unicos usuarios reales).
- Los usuarios de prueba (`Vendedor test`, `vendedor`) quedan en el default
  seguro, para no dejar datos invalidos que alguien use por error.

Idempotente: solo toca filas cuyo seller_types todavia menciona el valor legacy.

Revision ID: d3f4a5b6c7d8
Revises: a6b7c8d9e0f1
Create Date: 2026-10-02

"""
import sqlalchemy as sa
from alembic import op

revision = "d3f4a5b6c7d8"
down_revision = "a6b7c8d9e0f1"
branch_labels = None
depends_on = None

LEGACY = "vendedor_interno"


def upgrade() -> None:
    bind = op.get_bind()
    users = sa.table("users", sa.column("username"), sa.column("seller_types", sa.JSON))
    stale = users.c.seller_types.cast(sa.Text).like(f"%{LEGACY}%")

    bind.execute(
        users.update()
        .where(users.c.username == "admin", stale)
        .values(seller_types=["representante_general", "representante_agro"])
    )
    bind.execute(
        users.update()
        .where(users.c.username != "admin", stale)
        .values(seller_types=["representante_general"])
    )


def downgrade() -> None:
    # No-op a proposito: `vendedor_interno` ya no es un seller_type valido
    # (migracion b4c5d6e7f8a9). Restaurarlo devolveria a los usuarios al bug
    # que esta migracion arregla. Mismo criterio que b4c5d6e7f8a9.
    pass