import pytest

from app.utils.cuit import validar_cuit


def _cuit(prefijo: str, verificador: str) -> str:
    return f"{prefijo}{verificador}"


@pytest.mark.parametrize("cuit", [
    _cuit("3000000000", "7"),
    _cuit("3060000000", "0"),
    _cuit("2090000000", "7"),
    _cuit("2700000000", "6"),
    "20123456786",
])
def test_cuit_validos(cuit):
    assert validar_cuit(cuit) is True


@pytest.mark.parametrize("cuit", [
    "2012345678",        # 10 dígitos
    "201234567890",      # 12 dígitos
    "20123456780",       # dígito verificador incorrecto
    "20900000009",       # dígito verificador incorrecto
    "abcdefghijk",       # no numérico
    "",
    None,
    "30-00000000-6",     # formato con guiones y verificador incorrecto
    "30.00000000.6",     # formato con puntos y verificador incorrecto
])
def test_cuit_invalidos(cuit):
    assert validar_cuit(cuit) is False


@pytest.mark.parametrize("cuit", [
    "30-00000000-7",
    "30.00000000.7",
    "30 00000000 7",
    " 20123456786 ",
])
def test_cuit_formateados_validos(cuit):
    assert validar_cuit(cuit) is True
