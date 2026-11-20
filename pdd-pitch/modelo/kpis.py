"""Calcula KPIs y múltiplos de PDD por ADS a partir de datos/cifras_verificadas.json.

Todo se expresa en RMB millones salvo indicación. Los valores 'no_resuelto' se marcan
como tales y no se usan en cálculos.
Salida: salidas/kpis.md
"""
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((RAIZ / "datos" / "cifras_verificadas.json").read_text(encoding="utf-8"))


def v(x):
    return x["valor"] if isinstance(x, dict) else x


ing = d["ingresos"]
uo = d["utilidad_operativa_GAAP"]
un = d["utilidad_neta_atribuible"]
bal = d["balance_30sep2026"]
mkt = d["mercado"]

# Q4 2025 de comunicado (no está en el JSON): ingresos 123.9 bn, op. 27.7 bn
Q4_25_ING = 123912.2
Q4_25_UO = 27719.7

# --- Ingresos y utilidad operativa ---
ing_9m26 = v(ing["Q1_2026"]) + v(ing["Q2_2026"]) + v(ing["Q3_2026"])
ing_9m25 = v(ing["Q1_2025"]) + v(ing["Q2_2025"]) + v(ing["Q3_2025"])
fy25_ing = v(ing["FY2025"])
ttm_ing = fy25_ing + ing_9m26 - ing_9m25

uo_9m26 = v(uo["Q1_2026"]) + v(uo["Q2_2026"]) + v(uo["Q3_2026"])
uo_9m25 = v(uo["Q1_2025"]) + v(uo["Q2_2025"]) + v(uo["Q3_2025"])
fy25_uo = v(uo["FY2025"])
ttm_uo = fy25_uo + uo_9m26 - uo_9m25

# Chequeo: suma trimestral 2025 contra FY reportado
suma_ing_25 = v(ing["Q1_2025"]) + v(ing["Q2_2025"]) + v(ing["Q3_2025"]) + Q4_25_ING
suma_uo_25 = uo_9m25 + Q4_25_UO

# --- Acción y valoración ---
precio = mkt["precio_ADS_USD"]["valor"]
fx = mkt["tipo_cambio_CNY_por_USD"]["valor"]
ads_eq = mkt["ADS_equivalentes_millones"]["valor"]  # millones
cap_usd = precio * ads_eq  # millones USD
cap_cny = cap_usd * fx  # millones RMB

caja = v(bal["caja_mas_inversiones"])
deuda = v(bal["deuda_financiera"]) if isinstance(bal["deuda_financiera"]["valor"], (int, float)) else 0
ev_cny = cap_cny - caja + deuda

# EPS TTM por ADS: utilidad neta TTM / ADS equivalentes
# Q2 2025 neta no está en el JSON: derivada de Q2 2026 (27.2 bn, -12% a/a)
q2_25_un = v(un["Q2_2026"]) / 0.88
ttm_un = v(un["FY2025"]) + (v(un["Q1_2026"]) + v(un["Q2_2026"]) + v(un["Q3_2026"])) - (
    v(un["Q1_2025"]) + q2_25_un + v(un["Q3_2025"])
)
eps_ttm_ads_cny = ttm_un / ads_eq
eps_ttm_ads_usd = eps_ttm_ads_cny / fx

# EPS forward por ADS (USD): Q1 y Q2 reportados, Q3 real aproximado (neta / ADS eq. / FX),
# Q4 estimado. Mezcla base no ajustada y consenso no GAAP: es una aproximación.
eps_q3_real_usd = v(un["Q3_2026"]) / ads_eq / fx
eps_fwd_usd = (
    mkt["EPS_ADS_Q1_2026_USD"]["valor"]
    + mkt["EPS_ADS_Q2_2026_USD"]["valor"]
    + eps_q3_real_usd
    + mkt["EPS_ADS_consenso_Q4_2026_USD"]["valor"]
)

kpis = [
    ("Ingresos TTM (RMB mn)", ttm_ing, "FY25 + 9M26 - 9M25"),
    ("Crec. ingresos 9M26 a/a", ing_9m26 / ing_9m25 - 1, "%"),
    ("Utilidad operativa TTM (RMB mn)", ttm_uo, "FY25 + 9M26 - 9M25"),
    ("Margen operativo TTM", ttm_uo / ttm_ing, "%"),
    ("Chequeo: suma trimestral 2025 ingresos", suma_ing_25, "vs FY25 431,846"),
    ("Chequeo: suma trimestral 2025 op.", suma_uo_25, "vs FY25 94,624"),
    ("Caja + inversiones 30sep26 (RMB mn)", caja, "sin restringida"),
    ("Caja neta por ADS (USD)", caja / ads_eq / fx, "caja / ADS eq. / FX"),
    ("Capitalización (USD mn)", cap_usd, f"precio {precio} x {ads_eq} mn ADS eq."),
    ("EV (RMB mn)", ev_cny, "cap - caja"),
    ("EV / EBIT TTM", ev_cny / ttm_uo, "x"),
    ("EPS TTM por ADS (USD)", eps_ttm_ads_usd, "utilidad neta TTM / ADS eq."),
    ("P/E TTM por ADS", precio / eps_ttm_ads_usd, "x; criterio < 25x"),
    ("EPS forward 2026 por ADS (USD)", eps_fwd_usd, "Q1-Q2 reportados, Q3 real aprox., Q4 consenso"),
    ("P/E forward por ADS", precio / eps_fwd_usd, "x; criterio < 25x"),
    ("OCF FY2025 / capitalización", v(d["ocf"]["FY2025"]) / cap_cny, "antes de capex (no resuelto)"),
    ("FCF yield / margen", "no_resuelto", "falta capex y OCF Q3 2026"),
]


def fmt(x):
    if isinstance(x, str):
        return x
    if abs(x) < 2 and not abs(x) < 1e-9 and "%" in str(x):
        return f"{x:.1%}"
    return f"{x:,.2f}"


lineas = [
    "# KPIs PDD Holdings (por ADS)",
    "",
    f"Precio de referencia: USD {precio} (cierre 2026-11-17). Tipo de cambio aproximado {fx} (no resuelto en FRED).",
    "Estado de las cifras y fuentes en `datos/cifras_verificadas.json`.",
    "",
    "| KPI | Valor | Nota |",
    "|---|---|---|",
]
for nombre, valor, nota in kpis:
    if isinstance(valor, str):
        texto = valor
    elif "Crec." in nombre or "Margen" in nombre or "yield" in nombre or "OCF" in nombre:
        texto = f"{valor:.1%}"
    elif "P/E" in nombre or "EV /" in nombre:
        texto = f"{valor:.1f}x"
    else:
        texto = f"{valor:,.2f}"
    lineas.append(f"| {nombre} | {texto} | {nota} |")

salida = RAIZ / "salidas" / "kpis.md"
salida.parent.mkdir(parents=True, exist_ok=True)
salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
