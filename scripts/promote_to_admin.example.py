"""
Script de una sola vez para promover un usuario existente a administrador.

USO:
  1. Copiar este archivo a promote_to_admin.py:
       cp promote_to_admin.example.py promote_to_admin.py

  2. Editar las variables abajo (DB_URL, USERNAME).

  3. Ejecutar:
       cd backend
       pip install sqlalchemy psycopg2-binary
       python ../scripts/promote_to_admin.py

  O con Docker:
       docker exec -it <container> python -c "$(cat ../scripts/promote_to_admin.py)"

SEGURIDAD: NO committear ni compartir la copia editada (promote_to_admin.py),
solo el template (.example.py). El .py final esta en .gitignore.
"""

# ─── CONFIGURACION ───────────────────────────────────────────────
DB_URL = "postgresql://appuser:apppassword@localhost:5432/authdb"
USERNAME = "nombre-del-usuario-a-promover"
# ─────────────────────────────────────────────────────────────────

from sqlalchemy import create_engine, text

if __name__ == "__main__":
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("UPDATE users SET role = 'admin' WHERE username = :username"),
            {"username": USERNAME},
        )
        conn.commit()
    print(f"Usuario '{USERNAME}' promovido a admin. Filas afectadas: {result.rowcount}")
