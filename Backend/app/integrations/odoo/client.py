import odoorpc
from ... import config


class OdooClient:
    def __init__(self):
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            self._connection = odoorpc.ODOO(
                config.settings.ODOO_URL.replace("https://", ""),
                port=443,
                protocol='jsonrpc+ssl',
            )
            self._connection.login(
                config.settings.ODOO_DB,
                config.settings.ODOO_USER,
                config.settings.ODOO_PASSWORD,
            )
        return self._connection


_default_client = OdooClient()


def get_odoo_connection():
    return _default_client.get_connection()
