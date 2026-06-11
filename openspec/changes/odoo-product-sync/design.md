# Design: Sincronización de Productos desde Odoo

## Arquitectura

Sigue el mismo modelo **Pull-based** con persistencia local implementado para clientes:

```
Odoo Online (product.template)
    │
    │  JSON-RPC via odoorpc
    ▼
Backend FastAPI (sync_products)
    │
    │  SQLAlchemy ORM
    ▼
PostgreSQL (products table)
    │
    │  REST API (JSON)
    ▼
Aplicación (Flutter u otros consumidores)
```

## Flujo de Datos

### 1. Sincronización (carga)
1. El endpoint `POST /sync/products` recibe una solicitud autenticada.
2. `sync_products()` se conecta a Odoo mediante `odoorpc`.
3. Consulta `product.template` con filtro `[('active', '=', True)]`.
4. Para cada producto, obtiene el nombre de categoría desde `categ_id` (tuple `(id, name)`).
5. Realiza `upsert` en la tabla `products` usando `odoo_id` como clave única.
6. Commit de la transacción.

### 2. Consulta (API)
- `GET /products` — Lista de productos con filtros opcionales por query params.
- `GET /products/{id}` — Detalle de un producto por ID local.

## Modelo de Datos

### Tabla `products`

| Campo            | Tipo   | Origen Odoo                | Notas                          |
|------------------|--------|----------------------------|--------------------------------|
| `id`             | PK int | —                          | ID local                       |
| `odoo_id`        | int    | `product.template.id`      | Unique, index                  |
| `name`           | str    | `name`                     | Nombre del producto            |
| `default_code`   | str    | `default_code`             | Código interno / SKU           |
| `barcode`        | str    | `barcode`                  | Código de barras               |
| `list_price`     | float  | `list_price`               | Precio de venta público        |
| `standard_price` | float  | `standard_price`           | Costo                          |
| `type`           | str    | `type`                     | product / service / consu      |
| `categ_id`       | str    | `categ_id (name)`          | Nombre de categoría            |
| `uom_id`         | str    | `uom_id (name)`            | Unidad de medida               |
| `description_sale` | str  | `description_sale`         | Descripción para ventas       |
| `active`         | bool   | `active`                   | Producto activo                |
| `sale_ok`        | bool   | `sale_ok`                  | Disponible para venta          |

### SQLAlchemy Model (`models.py`)

```python
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    odoo_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    default_code = Column(String, index=True)
    barcode = Column(String)
    list_price = Column(Float, default=0.0)
    standard_price = Column(Float, default=0.0)
    type = Column(String, default="product")
    categ_id = Column(String)
    uom_id = Column(String)
    description_sale = Column(String)
    active = Column(Boolean, default=True)
    sale_ok = Column(Boolean, default=True)
```

### Pydantic Schemas (`schemas.py`)

```python
class ProductBase(BaseModel):
    name: str
    default_code: Optional[str] = None
    barcode: Optional[str] = None
    list_price: Optional[float] = None
    standard_price: Optional[float] = None
    type: Optional[str] = "product"
    categ_id: Optional[str] = None
    uom_id: Optional[str] = None
    description_sale: Optional[str] = None
    active: Optional[bool] = True
    sale_ok: Optional[bool] = True

class ProductCreate(ProductBase):
    odoo_id: int

class ProductOut(ProductBase):
    id: int
    odoo_id: int
    model_config = {"from_attributes": True}
```

## API

| Método | Ruta               | Auth     | Descripción                          |
|--------|---------------------|----------|--------------------------------------|
| POST   | `/sync/products`    | JWT      | Activa sincronización manual         |
| GET    | `/products`         | JWT      | Lista productos con filtros opcionales |
| GET    | `/products/{id}`    | JWT      | Detalle de producto                  |

### Filtros para `GET /products`
- `search` — búsqueda por nombre (ILIKE).
- `categ_id` — filtrar por nombre de categoría.
- `active` — filtrar por estado activo (default `True`).
- `sale_ok` — filtrar por disponibilidad para venta (default `True`).

## Seguridad

- Todos los endpoints requieren autenticación JWT.
- No hay restricción por vendedor: cualquier usuario autenticado puede ver todos los productos.
- La sincronización solo pueden ejecutarla usuarios autenticados (sin restricción de rol por ahora).

## Impacto Arquitectónico

- Bajo: sigue el mismo patrón exacto que la sincronización de clientes.
- No requiere nuevas dependencias.
- No afecta tablas existentes.
- La sincronización de clientes y productos son independientes entre sí.
