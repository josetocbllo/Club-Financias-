# DCF PDD Holdings · base y escenarios

Fecha de valoración: 2026-11-20. Precio de referencia: USD 77.39 (cierre 17 nov 2026). Tipo de cambio 6.8 (aproximado). ADS equivalentes: 1,480 mn (inferido).

## Supuestos clave
| Supuesto | Valor | Etiqueta |
|---|---|---|
| Tasa libre de riesgo | 4.5% | [Hipótesis] FRED no accesible |
| Beta | 1.00 | [Hipótesis] sin regresión calculada |
| Prima de mercado | 5.0% | [Hipótesis] |
| Prima país China | 1.0% | [Hipótesis] |
| Costo del capital = WACC | 10.5% | [Calculado] sin deuda |
| Crecimiento terminal | 2.5% | [Hipótesis] |
| Tasa efectiva de impuestos | 18.2% | [Calculado] XBRL FY2025 |
| Cuentas por pagar / ingresos | 7.6% | [Calculado] ΔCT = −7.6% × ΔIngresos |
| Capex y D&A / ingresos | 2.0% | [Hipótesis] no verificado |
| Ingresos 2026E | 457,008 | [Calculado] 9M26 real + Q4 con crecimiento 5% [Hipótesis] |
| Margen operativo de arranque | 24.0% | [Calculado] 9M26 |

## Escenarios
| Escenario | Margen 2031 | Crec. marketing 2027→2031 | Crec. transacción 2027→2031 | Valor por ADS (USD) | vs precio |
|---|---|---|---|---|---|
| bajista | 17% | 2%→2% | 3%→2% | 136.10 | +76% |
| base | 22% | 6%→3% | 10%→4% | 175.24 | +126% |
| alcista | 26% | 8%→4% | 15%→5% | 211.12 | +173% |

## Base · proyección y puente
| Año | Ingresos | Margen op. | EBIT | FCFF |
|---|---|---|---|---|
| 2027 | 493,410 | 23.6% | 116,619 | 98,177 |
| 2028 | 525,491 | 23.2% | 122,053 | 102,296 |
| 2029 | 551,846 | 22.8% | 125,918 | 105,026 |
| 2030 | 575,403 | 22.4% | 128,941 | 107,288 |
| 2031 | 595,634 | 22.0% | 131,039 | 108,753 |

- VP de flujos 2027–2031 + stub Q4 2026: RMB 429,197 mn
- VP del valor terminal: RMB 879,054 mn
- Valor operativo (EV): RMB 1,308,251 mn
- + Caja e inversiones: RMB 455,400 mn · − Deuda: RMB 0 mn (no_resuelto)
- = Valor del capital: RMB 1,763,651 mn
- Valor por ADS: USD 175.24
- Chequeo: EV + caja − deuda = capital (cuadra).
- Peso de la caja en el valor: 26% del capital.

## Reverse DCF
- Margen operativo 2031 que iguala el precio (crecimiento base): **2.1%** (base 22%, margen 9M26 24.0%).
- TIR implícita al precio (escenario base): **30.0%** frente a un costo de capital de 10.5%.

## Sensibilidad 1 · WACC × crecimiento terminal (escenario base, USD por ADS)
| WACC \ g | 1.5% | 2.5% | 3.5% |
|---|---|---|---|
| 9.5% | 179.01 | 192.91 | 211.45 |
| 10.5% | 164.78 | 175.24 | 188.70 |
| 11.5% | 153.40 | 161.50 | 171.63 |
| 12.5% | 144.08 | 150.50 | 158.34 |

## Sensibilidad 2 · crecimiento marketing × transacción (puntos sobre la base, USD por ADS)
| Marketing \ Transacción | -5% | +0% | +5% |
|---|---|---|---|
| -3% | 154.06 | 167.37 | 183.40 |
| +0% | 161.93 | 175.24 | 191.27 |
| +3% | 170.75 | 184.06 | 200.09 |

## Sensibilidad 3 · margen operativo 2031 (escenario base, USD por ADS)
| Margen 2031 | Valor por ADS | vs precio |
|---|---|---|
| 18% | 155.61 | +101% |
| 20% | 165.43 | +114% |
| 22% | 175.24 | +126% |
| 24% | 185.06 | +139% |
| 26% | 194.88 | +152% |

## Sensibilidad 4 · descuento a la caja (escenario base)
La caja pesa mucho en el valor. Este bloque muestra cuánto cambia si no toda es disponible para el accionista (restricciones, repatriación desde China).
| Descuento a la caja | Valor por ADS (USD) | vs precio | Margen 2031 que iguala el precio |
|---|---|---|---|
| 0% | 175.24 | +126% | 2.1% |
| 25% | 163.93 | +112% | 4.4% |
| 50% | 152.62 | +97% | 6.7% |

## No capturado por el modelo
- Consenso de ingresos y EPS del año próximo: no verificado, no calibrado.
- Capex real, D&A por segmento y OCF de Q3 2026: no_resuelto.
- Tasa libre de riesgo, beta y prima país: hipótesis, no medidas.
- Caja en China: el modelo usa caja completa, sin descuento por repatriación.
- Deuda financiera y participaciones minoritarias: asumidas en cero.
- Tipo de cambio: aproximado. Cada 1% de cambio mueve el valor en USD en la misma proporción.
