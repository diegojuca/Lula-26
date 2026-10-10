"""Unidades Básicas de Saúde (Ministério da Saúde, API de dados abertos): nome, bairro, coordenadas, município.
Saída: raw/series/ubs.csv
"""
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "raw" / "series" / "ubs.csv"
API = "https://apidadosabertos.saude.gov.br/assistencia-a-saude/unidade-basicas-de-saude"
linhas, off = [], 0
while True:
    for t in range(8):
        try:
            js = requests.get(API, params={"limit": 1000, "offset": off}, timeout=120).json()["ubs"]
            break
        except Exception:
            time.sleep(min(60, 2 ** t))
    else:
        raise SystemExit(f"falhou em {off}")
    if not js:
        break
    linhas += js
    off += len(js)
pd.DataFrame(linhas).to_csv(OUT, index=False)
print("✓ UBS", len(linhas))
