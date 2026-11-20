"""Descarga XBRL de PDD Holdings desde SEC (companyfacts) y guarda crudos con fecha.

Uso:
    SEC_USER_AGENT="Nombre Apellido correo@dominio" python3 modelo/datos.py

Sin SEC_USER_AGENT usa un valor genérico; SEC pide un contacto real en el User-Agent.
"""
import datetime as dt
import json
import os
import pathlib
import urllib.request

CIK = "0001737806"  # PDD Holdings Inc.
RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
UA = os.environ.get("SEC_USER_AGENT", "pdd-pitch-research/1.0 (contacto no configurado)")
HOY = dt.date.today().isoformat()


def bajar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"
    crudo = bajar(url)
    destino = DATOS / f"companyfacts_{HOY}.json"
    destino.write_bytes(crudo)
    facts = json.loads(crudo)
    print(f"Guardado: {destino} ({len(crudo)/1e6:.2f} MB)")
    print("Entidad:", facts.get("entityName"))
    cnf = facts.get("facts", {}).get("us-gaap", {})
    print("Conceptos us-gaap:", len(cnf))


if __name__ == "__main__":
    main()
