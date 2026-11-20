---
name: zoom-tesis-equity
description: Zoom de tesis sobre una empresa a partir de su ticker: mapa competitivo, crédito, ruido vs debilidades, DCF con reverse DCF, pre-mortem con kill criteria, catalyst map y puntos para comité. Corre solo con fuentes gratuitas (SEC EDGAR/XBRL, Yahoo Finance, FRED; Finnhub opcional).
---

# Zoom de tesis sobre un ticker

El usuario entrega un ticker (y, opcionalmente, su tesis o sus preguntas). Tú entregas un documento de research listo para comité, en español, con cada afirmación etiquetada y cada número verificable. El DCF sirve para leer expectativas (qué descuenta el precio), no para fijar un precio objetivo. No emitas recomendaciones de compra o venta.

## Entradas

- **Ticker** (obligatorio).
- **Tesis o preguntas del usuario** (opcional). Si vienen, se responden primero y se contrastan con los datos: señala con claridad dónde no se sostienen.
- **Criterios de aceptación** (opcional). Por defecto:
  - P/E menor a 25x (forward con consenso y operativo TTM)
  - Flujo de caja libre mayor a 10% y positivo (como yield y como margen)
  - Moat
  - Balance fortaleza
  - Altas barreras de entrada
  - Líneas de negocio con crecimiento futuro

Si falta algo no esencial, asume, decláralo en una línea y sigue.

## Convenciones (obligatorias)

- Etiqueta cada afirmación relevante: **[Hecho]** (filing o dato de mercado), **[Calculado]** (aritmética propia sobre hechos), **[Atribución]** (prensa o terceros), **[Inferencia]** (razonamiento propio), **[Hipótesis]** (supuesto del modelo).
- Lo que no se pudo verificar queda como `no_resuelto`, con el motivo. Nunca rellenes con memoria.
- Periodos: etiqueta fiscal más meses calendario cuando difieren ("Q1 FY27 (jul–sep 2026)").
- Separa siempre lo que dice un 8-K o 10-Q (hecho) de lo que dice la prensa (atribución).
- Comparaciones entre empresas (spreads, márgenes, múltiplos): verifica que ambas cifras vengan de una fuente y del mismo concepto antes de escribirlas.
- Unidades: USD bn; decimales con coma; miles con punto.

## Proceso

### 1. Esqueleto primero

Crea el documento con título, byline (fecha y autor) y una línea de lead provisoria. Agrega un bloque pendiente por sección (ver "Estructura del documento"). Si el usuario ya tiene un dossier de la empresa, agrega una pestaña nueva en vez de un documento nuevo, y enlázala desde la pestaña principal.

### 2. Datos

Todo el flujo corre con fuentes públicas y gratuitas: **SEC EDGAR (XBRL)** para estados financieros y ratios, **Yahoo Finance** para precio, consenso y beta, **FRED/Treasury** para la tasa a 10 años y **Finnhub** (opcional, key gratuita) como control cruzado. No se necesita ninguna API key de pago. Baja los datos de mercado y estados para la empresa y 2–3 pares.

**Cómo llegar a cada fuente (en este orden):** Python (`requests`, `yfinance`) → WebFetch → navegador (abre la URL y extrae el texto o el JSON con un fetch dentro de la página). Si el entorno bloquea un dominio desde Python, el usuario puede permitirlo en Settings > Capabilities (dominios permitidos); mientras tanto, sigue con WebFetch o el navegador. Si una fuente falla tras un reintento, pasa al respaldo de la tabla; si ninguno responde, el dato queda `no_resuelto`.

| Dato | Fuente principal | Respaldo |
|---|---|---|
| Precio actual y trayectoria (diaria 1 año, semanal 5 años) | Yahoo: `yf.Ticker(T).history(...)` o `https://query1.finance.yahoo.com/v8/finance/chart/{T}?range=1y&interval=1d` | Finnhub `/quote` (solo precio actual); página de Yahoo en el navegador |
| Tasa a 10 años del día | FRED `DGS10`, sin key: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10` (último valor no vacío) | Yahoo `^TNX` (comprueba la escala: debe leerse como %, del orden de 3–5); Daily Treasury Par Yield Curve Rates en home.treasury.gov |
| Estado de resultados, balance y flujo de caja | SEC XBRL: `companyfacts` o `companyconcept` (ver abajo) | Tablas del 10-Q/10-K en EDGAR; Finnhub `/stock/financials-reported` |
| Acciones en circulación | `dei:EntityCommonStockSharesOutstanding` (portada del último filing) | Acciones diluidas del estado de resultados |
| Consenso de ingresos y EPS (año en curso y próximo) | Yahoo: `t.earnings_estimate`, `t.revenue_estimate`, `t.eps_trend` (filas `0y` y `+1y`) | `https://finance.yahoo.com/quote/{T}/analysis` en el navegador |
| Próxima fecha de resultados y sorpresas de EPS | Finnhub `/calendar/earnings`, `/stock/earnings` | Yahoo `t.calendar`, `t.earnings_dates`; IR de la empresa |
| Beta | Calculada por ti: regresión de retornos semanales (2–5 años) contra `^GSPC`, con precios de Yahoo | Yahoo `t.info["beta"]`; Finnhub `/stock/metric` |
| Pares candidatos | Finnhub `/stock/peers`; código SIC en `submissions` | Criterio propio, declarado |

- **Ritmo de llamadas:** en serie, nunca en paralelo. SEC: máximo 10 por segundo y header `User-Agent` con nombre y correo (sin él responde 403; usa `SEC_USER_AGENT` si existe y, si no, pide nombre y correo al usuario una vez). Yahoo es una fuente no oficial: pausa de 1–2 s entre llamadas y, ante un 429 o un error de "crumb", usa el endpoint `chart` o el navegador. Finnhub: 60 por minuto con key gratuita (`FINNHUB_API_KEY`); sin key, omite Finnhub y usa los respaldos.
- **Ratios de terceros:** los múltiplos de Yahoo (`info`) o Finnhub (`/stock/metric`) son solo control cruzado. Los múltiplos del documento los calculas tú desde filings y precio, y van como **[Calculado]**. Si tu cálculo difiere más de 10% del de terceros, explica la diferencia (definición o periodo) antes de publicarlo.
- **SEC EDGAR, endpoints:**
  - Ticker → CIK: `https://www.sec.gov/files/company_tickers.json` (CIK a 10 dígitos, con ceros a la izquierda).
  - Lista de filings, SIC y cierre fiscal: `https://data.sec.gov/submissions/CIK##########.json`.
  - Todos los conceptos XBRL: `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` (pesa varios MB: úsalo desde Python).
  - Un concepto: `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/{Etiqueta}.json` (liviano: úsalo con WebFetch o el navegador).
  - Un concepto para todas las empresas en un periodo: `https://data.sec.gov/api/xbrl/frames/us-gaap/{Etiqueta}/USD/CY2026Q2.json` (flujos) o `CY2026Q2I` (saldos). Sirve para comparar pares sobre el mismo concepto.
  - Documento: `https://www.sec.gov/Archives/edgar/data/{CIK sin ceros}/{accession sin guiones}/{primaryDocument}`.
- **Etiquetas XBRL** (prueba en orden y registra cuál usaste; cambian entre empresas y años):

| Concepto | Etiquetas us-gaap |
|---|---|
| Ingresos | `RevenueFromContractWithCustomerExcludingAssessedTax`, `Revenues`, `SalesRevenueNet` |
| Resultado operativo | `OperatingIncomeLoss` |
| Utilidad neta | `NetIncomeLoss` |
| EPS diluido y acciones diluidas | `EarningsPerShareDiluted` (USD/shares); `WeightedAverageNumberOfDilutedSharesOutstanding` (shares) |
| Impuestos | `IncomeTaxExpenseBenefit`; `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` |
| Gasto por intereses | `InterestExpense`, `InterestExpenseNonoperating`, `InterestExpenseDebt` |
| D&A | `DepreciationDepletionAndAmortization`, `DepreciationAmortizationAndAccretionNet`, `DepreciationAndAmortization` |
| SBC | `ShareBasedCompensation`, `AllocatedShareBasedCompensationExpense` |
| Flujo operativo y capex | `NetCashProvidedByUsedInOperatingActivities`; `PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsToAcquireProductiveAssets` |
| Recompras y emisiones | `PaymentsForRepurchaseOfCommonStock`; `ProceedsFromIssuanceOfCommonStock` |
| Caja y valores | `CashAndCashEquivalentsAtCarryingValue`; `MarketableSecuritiesCurrent`, `AvailableForSaleSecuritiesDebtSecuritiesCurrent`, `ShortTermInvestments` |
| Deuda | `LongTermDebt`; `LongTermDebtCurrent` + `LongTermDebtNoncurrent`; `ShortTermBorrowings`, `CommercialPaper` |
| Patrimonio, minoritario, preferentes | `StockholdersEquity`; `MinorityInterest`; `PreferredStockValue` |
| PP&E y activos no puestos en servicio | `PropertyPlantAndEquipmentNet`; `ConstructionInProgressGross` |
| Backlog u obligaciones de desempeño | `RevenueRemainingPerformanceObligation` |
| Ganancias en valores | `EquitySecuritiesFvNiGainLoss`, `GainLossOnInvestments` |

- **Reglas XBRL:**
  - `fy` y `fp` describen el filing, no el periodo: un 10-K repite años anteriores con el mismo `fy`. Identifica cada periodo por `start` y `end`, y si un periodo aparece en varios filings, usa el de `filed` más reciente (recoge reexpresiones).
  - En los 10-Q, el flujo de caja viene acumulado en el año (YTD). Trimestre = YTD actual − YTD anterior; Q4 = anual del 10-K − 9 meses. TTM = suma de los últimos cuatro trimestres consecutivos.
  - `companyfacts` no trae segmentos ni la mayoría de las notas (dimensiones XBRL). Segmentos, D&A por segmento, garantías y cláusulas se leen en el texto del filing.
  - Unidades: `USD`, `USD/shares`, `shares`. Convierte a USD bn al escribir.
- **Ratios desde filings y precio (todos [Calculado]):**
  - Capitalización = precio × acciones de portada. EV = capitalización + deuda + preferentes + interés minoritario − caja y valores.
  - P/E operativo TTM = precio / EPS operativo TTM, donde EPS operativo = utilidad neta TTM sin ganancias en valores ni partidas no recurrentes (netas de impuesto a la tasa declarada) / acciones diluidas. P/E forward = precio / EPS de consenso del próximo año fiscal (Yahoo).
  - FCF = flujo operativo − capex (TTM). FCF yield = FCF / capitalización. Margen FCF = FCF / ingresos.
  - EBITDA = resultado operativo + D&A. Caja neta, deuda/EBITDA y cobertura = resultado operativo / gasto por intereses.
- **Código base** (guárdalo con el modelo y adáptalo):

```python
import requests, pandas as pd, yfinance as yf
UA = {"User-Agent": "Nombre Apellido correo@dominio.com"}  # obligatorio para SEC

def cik(ticker):
    m = requests.get("https://www.sec.gov/files/company_tickers.json", headers=UA).json()
    return next(f"{v['cik_str']:010d}" for v in m.values() if v["ticker"] == ticker.upper())

def serie(facts, etiquetas, unidad="USD", ns="us-gaap"):
    """Primera etiqueta disponible; un valor por periodo (el último presentado)."""
    for e in etiquetas:
        d = facts["facts"].get(ns, {}).get(e, {}).get("units", {}).get(unidad)
        if d:
            df = pd.DataFrame(d)
            df = df[df["form"].isin(["10-K", "10-Q", "10-K/A", "10-Q/A"])].copy()
            df["end"] = pd.to_datetime(df["end"])
            claves = ["end"]
            if "start" in df:
                df["start"] = pd.to_datetime(df["start"])
                df["dias"] = (df["end"] - df["start"]).dt.days
                claves = ["start", "end"]
            df = df.sort_values("filed").drop_duplicates(claves, keep="last")
            return e, df.sort_values("end").reset_index(drop=True)
    return None, None

def trimestres(df):
    """Flujos: trimestres discretos desde valores de 3 meses, YTD y anuales."""
    out = df[df.dias.between(80, 100)].set_index("end")["val"].to_dict()
    for _, r in df[df.dias.between(170, 375)].iterrows():
        if r.end in out:
            continue
        prev = df[(df.start == r.start) & (df.end < r.end)].sort_values("end")
        if len(prev):
            out[r.end] = r.val - prev.iloc[-1].val
    return pd.Series(out).sort_index()

def ttm(q):
    u = q.iloc[-4:]
    assert u.index.to_series().diff().dt.days.dropna().between(80, 100).all(), "trimestres no consecutivos"
    return u.sum()

c = cik("NVDA")
facts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{c}.json", headers=UA).json()
etq, cfo = serie(facts, ["NetCashProvidedByUsedInOperatingActivities"])
cfo_ttm = ttm(trimestres(cfo))
_, acciones = serie(facts, ["EntityCommonStockSharesOutstanding"], "shares", ns="dei")
t = yf.Ticker("NVDA")
precio = t.history(period="5d")["Close"].iloc[-1]
consenso_eps, consenso_ing = t.earnings_estimate, t.revenue_estimate
tasa10 = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10", na_values=".").dropna().iloc[-1]
```

- **Filings (EDGAR):** último 10-Q o 10-K y el 8-K de resultados (Ex. 99.1), localizados con `submissions` y leídos en su texto; las cifras de los estados salen de XBRL y se cruzan con el texto. Si WebFetch no llega a sec.gov, usa el navegador y extrae el texto con un fetch dentro de la página. Si registras un hash, hashea texto normalizado: los bytes crudos de EDGAR cambian entre lecturas.
- **Qué extraer del filing:** ingresos y resultado operativo por segmento; gastos por segmento; D&A y capex trimestrales; PP&E en servicio frente a activos aún no puestos en servicio; caja, valores, deuda, preferentes e interés minoritario; inversiones en patrimonio (valor razonable frente a measurement alternative); ganancias en valores que inflan la utilidad neta; garantías, compromisos y cláusulas de recompra; acciones diluidas; recompras y emisiones del periodo; backlog u obligaciones de desempeño.
- **Pares (4–5):** último trimestre de la línea comparable, backlog o RPO, capex, flujo de caja libre, rating, insumo crítico y contraparte que concentra. Abre los comunicados o filings; un snippet de búsqueda no es fuente.
- **Evento reciente:** si hay uno que mueva la tesis (cambio de CEO, regulación, contrato), busca el 8-K o comunicado oficial y luego la prensa.

### 3. Modelo (Python, corrido y guardado)

Principios: el modelo es un instrumento de pensamiento; los ingresos se construyen por drivers operativos reales; se trabaja con tres drivers; los históricos vienen de filings; el modelo debe ser simple, flexible y auditable.

- **Año en curso:** acumulado real más trimestres restantes estimados. Compara con el consenso de ingresos.
- **Ingresos** por segmento, con crecimiento año a año. Identifica los **tres drivers** que más mueven el valor.
- **Márgenes** EBITDA por segmento. Si el filing no divulga D&A por segmento, reparte la D&A con una hipótesis explícita y decláralo.
- **Capex y D&A** (crítico en negocios intensivos en activos): motor de depreciación por cosechas trimestrales, con mezcla de vidas útiles (equipos y edificios) y rezago de puesta en servicio. Calíbralo contra la D&A reportada y los activos no puestos en servicio, y aplica un factor de calibración que iguale el acumulado del año.
- **FCFF** = EBIT × (1 − tasa) + D&A − capex − Δcapital de trabajo (+ diferimiento fiscal por depreciación acelerada si aplica). La compensación en acciones (SBC) es costo: no se suma de vuelta.
- **WACC** con la tasa a 10 años del día, beta y prima explícitas. Crecimiento terminal explícito. Descuento a mitad de año. Flujo del periodo entre el último balance y el cierre del año (stub) en el puente.
- **Puente:** valor operativo + caja y valores de deuda + participaciones netas de impuesto diferido − deuda − preferentes − interés minoritario.
- **Salidas obligatorias:**
  - Valor por acción y TIR implícita al precio de hoy.
  - Escenarios bajista, base, alcista y "consenso" (calibrado a ingresos y EPS de consenso del próximo año fiscal).
  - Reverse DCF: un driver a la vez, más el múltiplo de salida implícito frente al del crecimiento terminal.
  - Tres grillas de sensibilidad: WACC × g; driver 1 × driver 2; driver 3.
  - EPS del próximo año del modelo frente al consenso, con la razón de la diferencia.
- Verifica por script que el puente cuadra y que cada número del documento sale del output. Guarda el código en el proyecto.

### 4. Escritura

Una sección por llamada: primero la prosa, después los diagramas. Cada sección abre con su conclusión y un número. Oraciones cortas; tablas para atributos de distinto tipo; diagramas para formas (matriz competitiva, línea de tiempo).

### 5. Revisión

Relee como un PM exigente:

- ¿Algún número sin fuente?
- ¿Alguna comparación sin verificar?
- ¿Algún "[Hecho]" que en realidad es prensa?

Toma captura de cada diagrama y corrige textos cortados o fuera de caja.

## Estructura del documento

1. **Lead:** una oración con la respuesta y el número (por ejemplo, "X es el líder en Y, pero a $P el precio descuenta Z: DCF base $V y TIR implícita T%").
2. **Respuesta corta:** las preguntas del usuario respondidas en 2–3 oraciones cada una, más una pregunta obligatoria: "¿está más barata que antes?", con la trayectoria del precio. Incluye la tabla de criterios de aceptación (Criterio | Umbral | Dato | Resultado). Advierte si el P/E GAAP está distorsionado (ganancias en valores, partidas no recurrentes) y usa el P/E operativo.
3. **Mapa competitivo:** diagrama de matriz con las capas de la cadena de valor relevantes para la industria (filas) por jugador (columnas). Estados: propio a escala / parcial o con terceros / no tiene. Debajo, filas de riesgo: rating y dependencia clave. El título del diagrama es el hallazgo.
4. **Pares:** tabla Jugador | Último trimestre | Backlog/RPO | Capex | FCF | Rating | Insumo crítico | Contraparte que concentra. Agrega las salvedades de comparabilidad y el P/E forward con consenso.
5. **Financiamiento y crédito:** tabla (caja, deuda, caja neta, deuda/EBITDA, cobertura, rating, contingentes). Bullets sobre spreads, la brecha de financiamiento del próximo año y el cambio en la asignación de capital (recompras frente a emisión).
6. **Evento reciente** (si existe): hechos del filing; atribución de prensa; tabla Área | Efecto esperado | Por qué; qué mirar en el próximo hito.
7. **Ruido frente a puntos que se pueden debilitar:** tabla Tema | Veredicto (ruido / real / real lento) | Dato | Área. Abre con una oración sobre qué es lo que realmente puede debilitarse.
8. **DCF:** puente al valor por acción, proyección anual, escenarios, reverse DCF y tres grillas de sensibilidad.
9. **Supuestos:** tabla Bloque | Supuesto | Valor | Etiqueta | Fuente o razón, con todos los supuestos. Cierra con "lo que el modelo no captura".
10. **Pre-mortem y kill criteria:** "Es [fecha +2 años] y la acción cayó 40%". Escribe 6–8 historias en tabla: # | Cómo falló | Señal temprana | Kill criterion (umbral medible) | Dónde se ve | Hoy. Separa una alerta de valoración (TIR implícita a precios más altos), distinta de los kill criteria de tesis. Cierra con una regla de uso: uno cruzado obliga a rehacer su driver; dos cruzados obligan a volver a comité.
11. **Catalyst map:** diagrama de carriles (empresa, cadena o pares, contraparte clave, macro y regulación) por mes, a 6–8 meses. Destaca el catalizador principal y marca con borde punteado las fechas inciertas. Debajo, tabla Catalizador | Confirma | Daña | Kill criterion ligado. Fechas no confirmadas: "por patrón histórico".
12. **Puntos para comité:** 6–8 bullets; cada uno una afirmación con su número y su etiqueta.
13. **Fuentes:** primarias; datos de mercado (fuente, endpoint y fecha y hora de captura; Yahoo es no oficial); prensa (atribución); lista de `no_resuelto`; ubicación del código del modelo.

## Respuesta en el chat

Al terminar, en el chat:

- Una línea con el enlace al documento.
- Las respuestas cortas a las preguntas del usuario.
- Dónde no coinciden los datos con su tesis.
- Un siguiente paso natural.

No repitas el documento.

## Errores que esta skill evita

- Leer el P/E GAAP de una empresa con grandes participaciones como si fuera el operativo.
- Comparar segmentos que incluyen cosas distintas (una nube que incluye venta de hardware frente a una que no).
- Publicar una comparación entre pares sin verificar que ambas cifras miden lo mismo.
- Suponer que la D&A sigue al capex sin rezago: los activos no puestos en servicio se deprecian después.
- Tratar un backlog como ingreso garantizado sin mirar la concentración y la capacidad de pago de la contraparte.
- Confundir la caída del flujo de caja en fase de inversión con deterioro del negocio (o al revés).
