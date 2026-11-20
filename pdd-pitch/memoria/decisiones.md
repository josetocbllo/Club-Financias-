# Decisiones y supuestos · PDD pitch

| Fecha | Decisión o supuesto | Quién lo aprobó | Estado |
|---|---|---|---|
| 2026-11-20 | Fuente primaria de cifras anuales: XBRL companyfacts (20-F) vía data.sec.gov. | Pendiente de aprobación | Activo |
| 2026-11-20 | Trimestres 2026: fuentes secundarias (prensa que cita el comunicado). El 6-K oficial devolvió 403. | Pendiente | Activo |
| 2026-11-20 | Precio de referencia USD 77.39 (cierre 17 nov). No se encontró el cierre del 19 nov. | Pendiente | Activo |
| 2026-11-20 | Tipo de cambio 6.8 CNY/USD, aproximado. FRED no accesible. | Pendiente | Reemplazar con DEXCHUS |
| 2026-11-20 | ADS equivalentes 1,480 mn inferidos (utilidad neta FY25 / EPS diluido por ADS). | Pendiente | Verificar con 20-F |
| 2026-11-20 | Utilidad operativa FY2025 = 94.6 bn (comunicado), no 93.1 bn (XBRL). | Pendiente | Diferencia sin resolver |
| 2026-11-20 | User-Agent de SEC genérico. Configurar `SEC_USER_AGENT` con contacto real antes de uso formal. | Usuario | Pendiente |
| 2026-11-20 | Ajustes de la skill (20-F/6-K, CNY, ADS de 4) aplicados en el modelo, no en SKILL.md (no se encontró el archivo de skill en el repositorio). | Pendiente | Pendiente |

## Preguntas abiertas
- ¿Cómo se trata la caja retenida en China en el puente del DCF?
- ¿Se usa EV/EBIT o P/E ex-caja como múltiplo principal?
