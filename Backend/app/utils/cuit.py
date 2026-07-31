import re


def validar_cuit(cuit: str) -> bool:
    """Valida un CUIT/CUIL argentino: 11 dígitos + dígito verificador (algoritmo mod-11 de AFIP)."""
    if not cuit:
        return False
    cuit = re.sub(r"[\s\-.]", "", cuit)
    if not cuit.isdigit() or len(cuit) != 11:
        return False

    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(cuit[i]) * weights[i] for i in range(10))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        check = 0
    elif check == 10:
        return False

    return check == int(cuit[10])
