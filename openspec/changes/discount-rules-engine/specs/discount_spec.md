# Spec: Reglas de Descuento

## Matriz de descuentos

### Tramos por monto (sin impuestos)
| Tramo | Interno | General | Agro |
|---|---|---|---|
| < USD 500 | 0% | 0% | 0% |
| < USD 5.000 | 11% | 11% | 5% |
| < USD 10.000 | 11-20% | 11-20% | 15% |
| 10k - 50k | mismo tramo 10k | mismo tramo 10k | mismo tramo 10k |
| > USD 50.000 | 15-30% | 15-30% | 15-30% |

### Tramos por cantidad (paneles, pallet=36u)
| Tramo | Interno | General | Agro |
|---|---|---|---|
| 1-17 u | 0% | 0% | 0% |
| 18-35 u (medio) | 11% | 11% | 5% |
| 36-179 u (pallet) | 11% | 11% | 15% |
| 180-359 u (5 pallets) | 15% | 15% | 15% |
| 360-719 u (10 pallets) | 20% | 20% | 20% |
| 720+ (container) | a convenir | a convenir | a convenir |

### KIT
- 20% para todas las líneas (inactivo en v1, Odoo no lo implementa).

### Campaña
- "a convenir" → requiere aprobación manual.

## Evaluación
- Monto: precios de lista × cantidad, sin descuento.
- Tramo 10k aplica para 10k-50k.
- Regla más restrictiva gana.
