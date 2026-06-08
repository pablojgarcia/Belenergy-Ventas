import pytest
import pytest
import sys
import os

# Asegurar que el directorio raíz del proyecto está en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.odoo_sync import get_odoo_connection
from app.config import settings

def test_odoo_connection_basic():
    """Valida que la conexión inicial y el servidor sean accesibles."""
    try:
        odoo = get_odoo_connection()
        # En odoorpc, odoo.version retorna un string con la versión
        info = odoo.version
        assert info is not None
        assert isinstance(info, str)
    except Exception as e:
        pytest.fail(f"La conexión a Odoo falló: {e}")

def test_odoo_partner_access():
    """Valida que tenemos permisos para listar al menos un cliente en Odoo."""
    try:
        odoo = get_odoo_connection()
        # Intentamos obtener un solo partner
        partner_ids = odoo.env['res.partner'].search([('customer_rank', '>', 0)], limit=1)
        assert isinstance(partner_ids, list)
    except Exception as e:
        pytest.fail(f"Error al acceder a los partners de Odoo: {e}")
