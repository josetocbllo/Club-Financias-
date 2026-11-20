"""DCF de PDD Holdings (FCFF) con escenarios, reverse DCF y grillas de sensibilidad.

Unidades: RMB millones salvo indicación. Valor final por ADS en USD.
Etiquetas: [Hecho] dato de filing o comunicado · [Calculado] aritmética sobre hechos ·
[Hipótesis] supuesto del modelo (no verificado).

Salida: salidas/dcf.md
"""
import datetime as dt
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
VAL = dt.date(2026, 11, 20)  # fecha de valoración

# --- Hechos ---------------------------------------------------------------
REV_9M26 = 106200 + 112400 + 108300          # [Hecho, prensa del comunicado] 326,900
EBIT_9M26 = 19600 + 27800 + 31200            # [Hecho, prensa del comunicado] 78,600
MKT_9M26 = 49900 + (112400 - 54700) + 59800  # [Calculado] marketing 167,400
TRX_9M26 = 56300 + 54700 + 48500             # [Calculado] transacción 159,500
Q4_25_REV = 123912.2                         # [Hecho, comunicado Q4 2025]
TAX = 21732.8 / 119575.3                     # [Calculado, XBRL FY2025] tasa efectiva ~18.2%
AP_FY25 = 32663.0                            # [Hecho, XBRL] cuentas por pagar
REV_FY25 = 431845.7                          # [Hecho, XBRL]
CASH = 455400                                # [Hecho, prensa] caja + inversiones 30 sep 2026
DEBT = 0                                     # [Hipótesis] sin deuda identificada; no_resuelto
ADS_EQ = 1480                                # [Inferido] millones de ADS equivalentes
FX = 6.8                                     # [Hipótesis] tipo de cambio aproximado
PRECIO = 77.39                               # [Hecho, prensa] cierre 17 nov 2026

# --- Supuestos ------------------------------------------------------------
G_Q4 = 0.05          # [Hipótesis] crecimiento de Q4 2026 vs Q4 2025
SPLIT_Q4 = 0.5       # [Hipótesis] reparto de Q4 entre marketing y transacción
WC_K = -AP_FY25 / REV_FY25  # [Calculado] ΔCT = WC_K × ΔIngresos (negativo: financiamiento de comerciantes)
CAPEX_PCT = 0.02     # [Hipótesis] capex / ingresos (no verificado; no_resuelto)
DA_PCT = 0.02        # [Hipótesis] D&A ≈ capex, como en la skill
RF = 0.045           # [Hipótesis] tasa 10 años; FRED no accesible
BETA = 1.0           # [Hipótesis] sin beta calculada
ERP = 0.05           # [Hipótesis] prima de mercado
CRP = 0.01           # [Hipótesis] prima país China
KE = RF + BETA * ERP + CRP   # sin deuda, WACC = Ke
G = 0.025            # [Hipótesis] crecimiento terminal
ANIOS = [2027, 2028, 2029, 2030, 2031]

ESCENARIOS = {
    "bajista": {"mkt": [0.02] * 5, "trx": [0.03, 0.02, 0.02, 0.02, 0.02], "m_T": 0.17},
    "base":    {"mkt": [0.06, 0.05, 0.04, 0.035, 0.03], "trx": [0.10, 0.08, 0.06, 0.05, 0.04], "m_T": 0.22},
    "alcista": {"mkt": [0.08, 0.07, 0.06, 0.05, 0.04], "trx": [0.15, 0.12, 0.09, 0.07, 0.05], "m_T": 0.26},
}

# --- Base 2026E -----------------------------------------------------------
Q4_26_REV = Q4_25_REV * (1 + G_Q4)
MKT_26 = MKT_9M26 + Q4_26_REV * SPLIT_Q4
TRX_26 = TRX_9M26 + Q4_26_REV * (1 - SPLIT_Q4)
REV_26 = REV_9M26 + Q4_26_REV
M_26 = EBIT_9M26 / REV_9M26                 # margen operativo 9M 2026 (usado para Q4 y arranque)
Q4_EBIT = Q4_26_REV * M_26


def _t(anio):
    """Años desde VAL hasta el punto medio del año (convención de mitad de año)."""
    return (dt.date(anio, 7, 1) - VAL).days / 365


def valor_por_ads(sc, wacc=KE, g=G, dm=0.0, dtr=0.0, m_T=None, detalle=False, haircut=0.0):
    """Valor por ADS en USD. dm y dtr suman puntos porcentuales al crecimiento de cada línea.
    haircut: fracción de la caja que no se considera disponible para el accionista (0 a 1)."""
    m_T = sc["m_T"] if m_T is None else m_T
    mkt, trx, rev_prev = MKT_26, TRX_26, REV_26
    t_stub = (dt.date(2026, 12, 31) - VAL).days / 365 / 2
    pv = Q4_EBIT * (1 - TAX) / (1 + wacc) ** t_stub     # flujo del stub Q4 2026
    filas = []
    ultimo = None
    for i, anio in enumerate(ANIOS):
        mkt *= 1 + sc["mkt"][i] + dm
        trx *= 1 + sc["trx"][i] + dtr
        rev = mkt + trx
        margen = M_26 + (m_T - M_26) * (i + 1) / len(ANIOS)
        ebit = rev * margen
        nopat = ebit * (1 - TAX)
        da = DA_PCT * rev
        capex = CAPEX_PCT * rev
        dct = WC_K * (rev - rev_prev)
        fcff = nopat + da - capex - dct
        t = _t(anio)
        pv += fcff / (1 + wacc) ** t
        filas.append((anio, rev, margen, ebit, fcff))
        rev_prev, ultimo, t_ult = rev, fcff, t
    tv = ultimo * (1 + g) / (wacc - g)
    pv_tv = tv / (1 + wacc) ** t_ult
    ev = pv + pv_tv
    eq = ev + CASH * (1 - haircut) - DEBT
    valor = eq / ADS_EQ / FX
    if detalle:
        return {"filas": filas, "pv_flujos": pv, "pv_tv": pv_tv, "ev": ev,
                "eq": eq, "valor": valor, "tv": tv}
    return valor


def biseccion(f, a, b, obj, n=100):
    """Busca x en [a, b] con f(x) = obj, asumiendo f decreciente o creciente monótona."""
    fa = f(a) - obj
    for _ in range(n):
        m = (a + b) / 2
        fm = f(m) - obj
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def main():
    lineas = []
    p = lambda s="": lineas.append(s)

    p("# DCF PDD Holdings · base y escenarios")
    p()
    p(f"Fecha de valoración: {VAL}. Precio de referencia: USD {PRECIO} (cierre 17 nov 2026). "
      f"Tipo de cambio {FX} (aproximado). ADS equivalentes: {ADS_EQ:,} mn (inferido).")
    p()
    p("## Supuestos clave")
    p("| Supuesto | Valor | Etiqueta |")
    p("|---|---|---|")
    p(f"| Tasa libre de riesgo | {RF:.1%} | [Hipótesis] FRED no accesible |")
    p(f"| Beta | {BETA:.2f} | [Hipótesis] sin regresión calculada |")
    p(f"| Prima de mercado | {ERP:.1%} | [Hipótesis] |")
    p(f"| Prima país China | {CRP:.1%} | [Hipótesis] |")
    p(f"| Costo del capital = WACC | {KE:.1%} | [Calculado] sin deuda |")
    p(f"| Crecimiento terminal | {G:.1%} | [Hipótesis] |")
    p(f"| Tasa efectiva de impuestos | {TAX:.1%} | [Calculado] XBRL FY2025 |")
    p(f"| Cuentas por pagar / ingresos | {-WC_K:.1%} | [Calculado] ΔCT = −7.6% × ΔIngresos |")
    p(f"| Capex y D&A / ingresos | {CAPEX_PCT:.1%} | [Hipótesis] no verificado |")
    p(f"| Ingresos 2026E | {REV_26:,.0f} | [Calculado] 9M26 real + Q4 con crecimiento {G_Q4:.0%} [Hipótesis] |")
    p(f"| Margen operativo de arranque | {M_26:.1%} | [Calculado] 9M26 |")
    p()

    p("## Escenarios")
    p("| Escenario | Margen 2031 | Crec. marketing 2027→2031 | Crec. transacción 2027→2031 | Valor por ADS (USD) | vs precio |")
    p("|---|---|---|---|---|---|")
    resultados = {}
    for nombre, sc in ESCENARIOS.items():
        v = valor_por_ads(sc)
        resultados[nombre] = v
        mk = "→".join(f"{x:.0%}" for x in (sc["mkt"][0], sc["mkt"][-1]))
        tr = "→".join(f"{x:.0%}" for x in (sc["trx"][0], sc["trx"][-1]))
        p(f"| {nombre} | {sc['m_T']:.0%} | {mk} | {tr} | {v:,.2f} | {v / PRECIO - 1:+.0%} |")
    p()

    p("## Base · proyección y puente")
    base = valor_por_ads(ESCENARIOS["base"], detalle=True)
    p("| Año | Ingresos | Margen op. | EBIT | FCFF |")
    p("|---|---|---|---|---|")
    for anio, rev, mg, ebit, fcff in base["filas"]:
        p(f"| {anio} | {rev:,.0f} | {mg:.1%} | {ebit:,.0f} | {fcff:,.0f} |")
    p()
    p(f"- VP de flujos 2027–2031 + stub Q4 2026: RMB {base['pv_flujos']:,.0f} mn")
    p(f"- VP del valor terminal: RMB {base['pv_tv']:,.0f} mn")
    p(f"- Valor operativo (EV): RMB {base['ev']:,.0f} mn")
    p(f"- + Caja e inversiones: RMB {CASH:,.0f} mn · − Deuda: RMB {DEBT:,.0f} mn (no_resuelto)")
    p(f"- = Valor del capital: RMB {base['eq']:,.0f} mn")
    p(f"- Valor por ADS: USD {base['valor']:,.2f}")
    # Verificación del puente por script
    assert abs(base["ev"] + CASH - DEBT - base["eq"]) < 1e-6, "el puente no cuadra"
    p(f"- Chequeo: EV + caja − deuda = capital (cuadra).")
    p(f"- Peso de la caja en el valor: {CASH / base['eq']:.0%} del capital.")
    p()

    p("## Reverse DCF")
    m_imp = biseccion(lambda m: valor_por_ads(ESCENARIOS["base"], m_T=m), 0.0, 0.6, PRECIO)
    p(f"- Margen operativo 2031 que iguala el precio (crecimiento base): **{m_imp:.1%}** "
      f"(base {ESCENARIOS['base']['m_T']:.0%}, margen 9M26 {M_26:.1%}).")
    w_imp = biseccion(lambda w: valor_por_ads(ESCENARIOS["base"], wacc=w), G + 0.005, 0.30, PRECIO)
    # valor decreciente en w: bisección con signo invertido
    lo, hi = G + 0.005, 0.30
    for _ in range(100):
        mid = (lo + hi) / 2
        if valor_por_ads(ESCENARIOS["base"], wacc=mid) > PRECIO:
            lo = mid
        else:
            hi = mid
    w_imp = (lo + hi) / 2
    p(f"- TIR implícita al precio (escenario base): **{w_imp:.1%}** frente a un costo de capital de {KE:.1%}.")
    p()

    p("## Sensibilidad 1 · WACC × crecimiento terminal (escenario base, USD por ADS)")
    waccs = [KE - 0.01, KE, KE + 0.01, KE + 0.02]
    gs = [0.015, 0.025, 0.035]
    p("| WACC \\ g | " + " | ".join(f"{x:.1%}" for x in gs) + " |")
    p("|---|" + "---|" * len(gs))
    for w in waccs:
        p(f"| {w:.1%} | " + " | ".join(f"{valor_por_ads(ESCENARIOS['base'], wacc=w, g=x):,.2f}" for x in gs) + " |")
    p()

    p("## Sensibilidad 2 · crecimiento marketing × transacción (puntos sobre la base, USD por ADS)")
    dms = [-0.03, 0.0, 0.03]
    dts = [-0.05, 0.0, 0.05]
    p("| Marketing \\ Transacción | " + " | ".join(f"{x:+.0%}" for x in dts) + " |")
    p("|---|" + "---|" * len(dts))
    for dm in dms:
        p(f"| {dm:+.0%} | " + " | ".join(f"{valor_por_ads(ESCENARIOS['base'], dm=dm, dtr=dt_):,.2f}" for dt_ in dts) + " |")
    p()

    p("## Sensibilidad 3 · margen operativo 2031 (escenario base, USD por ADS)")
    p("| Margen 2031 | Valor por ADS | vs precio |")
    p("|---|---|---|")
    for mT in [0.18, 0.20, 0.22, 0.24, 0.26]:
        v = valor_por_ads(ESCENARIOS["base"], m_T=mT)
        p(f"| {mT:.0%} | {v:,.2f} | {v / PRECIO - 1:+.0%} |")
    p()

    p("## Sensibilidad 4 · descuento a la caja (escenario base)")
    p("La caja pesa mucho en el valor. Este bloque muestra cuánto cambia si no toda es disponible para el accionista (restricciones, repatriación desde China).")
    p("| Descuento a la caja | Valor por ADS (USD) | vs precio | Margen 2031 que iguala el precio |")
    p("|---|---|---|---|")
    for h in [0.0, 0.25, 0.5]:
        v = valor_por_ads(ESCENARIOS["base"], haircut=h)
        mi = biseccion(lambda m: valor_por_ads(ESCENARIOS["base"], m_T=m, haircut=h), 0.0, 0.6, PRECIO)
        p(f"| {h:.0%} | {v:,.2f} | {v / PRECIO - 1:+.0%} | {mi:.1%} |")
    p()

    p("## No capturado por el modelo")
    p("- Consenso de ingresos y EPS del año próximo: no verificado, no calibrado.")
    p("- Capex real, D&A por segmento y OCF de Q3 2026: no_resuelto.")
    p("- Tasa libre de riesgo, beta y prima país: hipótesis, no medidas.")
    p("- Caja en China: el modelo usa caja completa, sin descuento por repatriación.")
    p("- Deuda financiera y participaciones minoritarias: asumidas en cero.")
    p("- Tipo de cambio: aproximado. Cada 1% de cambio mueve el valor en USD en la misma proporción.")

    salida = RAIZ / "salidas" / "dcf.md"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
