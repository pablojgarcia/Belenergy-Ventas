"""
Script de una sola vez para promover un usuario existente a administrador.

USO:
  1. Copiar este archivo a promote_to_admin.py (esta en .gitignore)
       cp promote_to_admin.example.py promote_to_admin.py

  2. Editar DB_URL y EMAIL con los valores reales.

  3. Ejecutar:
       pip install sqlalchemy psycopg2-binary
       python scripts/promote_to_admin.py

SEGURIDAD: NO committear ni compartir la copia editada (promote_to_admin.py).
Solo el template (.example.py) viaja en el repo.
"""

import sys

# ─── CONFIGURACION ───────────────────────────────────────────────
DB_URL = "postgresql://appuser:apppassword@localhost:5432/authdb"
EMAIL = "email-del-usuario"
# ─────────────────────────────────────────────────────────────────

from sqlalchemy import create_engine, text, inspect

if __name__ == "__main__":
    engine = create_engine(DB_URL)
    inspector = inspect(engine)

    if "users" not in inspector.get_table_names():
        print("ERROR: La tabla 'users' no existe.")
        sys.exit(1)

    cols = [c["name"] for c in inspector.get_columns("users")]
    if "role" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'vendedor'"))
        print("Columna 'role' creada.")

    with engine.begin() as conn:
        result = conn.execute(
            text("UPDATE users SET role = 'admin' WHERE email = :email AND role != 'admin'"),
            {"email": EMAIL},
        )
    print(f"Usuario '{EMAIL}' promovido a admin. Filas actualizadas: {result.rowcount}")
