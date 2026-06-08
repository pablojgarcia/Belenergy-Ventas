## Arquitectura

### Flujo actual

```
Frontend                      Backend                     PostgreSQL
   │                            │                            │
   ├── GET /customers ──────────►                            │
   │                            ├── SELECT * FROM customers ─►
   │                            │◄── todas las filas ───────┤
   │◄── todos los clientes ─────┤                            │
   │                            │                            │
   ├── filtrar por email ──────►│                            │
   │                            │                            │
```

### Nuevo flujo

```
Frontend                      Backend                     PostgreSQL
   │                            │                            │
   ├── GET /customers ──────────►                            │
   │                            ├── SELECT * FROM customers  │
   │                            │   WHERE salesperson_id IN  │
   │                            │   (:email, :name) ─────────►
   │                            │◄── filas filtradas ───────┤
   │◄── solo mis clientes ──────┤                            │
```

### Cambio en backend

**Archivo:** `Backend/app/main.py` — función `get_customers`

```python
@app.get("/customers", response_model=list[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Customer).filter(
        models.Customer.salesperson_id.in_([current_user.email, current_user.name])
    ).all()
```

Usar `.in_()` con `email` y `name` cubre el caso en que Odoo sincronice el identificador del vendedor como cualquiera de los dos valores.

### Frontend

No requiere cambios. El filtrado existente en `ClientesScreen._fetchClients()` se vuelve redundante pero inofensivo — se puede conservar como red de seguridad o eliminar en una limpieza posterior.

## Seguridad

- El filtrado ocurre a nivel de base de datos: un usuario no puede acceder a clientes de otro usuario aunque manipule la request
- El filtro usa la identidad del usuario autenticado del JWT, que no puede ser alterada

## Riesgos

- Si el `email` y `name` de un usuario difieren del `salesperson_id` almacenado en la DB, la consulta devuelve vacío. Mitigación: el filtro fallback del frontend aún existe y mostraría vacío — eso alertaría para investigar el mapeo de la sincronización.
