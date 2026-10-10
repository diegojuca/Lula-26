"""Série histórica do Mais Médicos por município (Ministério da Saúde, API de dados abertos), por UF.

Guarda, para cada município e ano, o total de profissionais ativos na última referência de dezembro
(no ano corrente, a última referência disponível). Saída: raw/series/mm_serie.csv
"""
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "raw" / "series"
API = "https://apidadosabertos.saude.gov.br/atencao-primaria/pmmb-serie-historica"
UFS = "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split()
linhas = []
for uf in UFS:
    off = 0
    while True:
        for t in range(8):
            try:
                js = requests.get(API, params={"uf": uf, "limit": 1000, "offset": off}, timeout=120).json()["pmmb_serie_historica"]
                break
            except Exception:
                time.sleep(min(60, 2 ** t))
        else:
            raise SystemExit(f"falhou {uf} {off}")
        if not js:
            break
        linhas += [(int(x["ibge"]) if x.get("ibge") else None, x["municipio_dsei"], uf, x["dt_referencia"], x["total_prof_ativos"]) for x in js]
        off += len(js)
    print(uf, off, flush=True)
d = pd.DataFrame(linhas, columns=["ibge6", "nome", "uf", "dt", "ativos"])
d["data"] = pd.to_datetime(d.dt, dayfirst=True)
d["ano"] = d.data.dt.year
ult = d.sort_values("data").groupby(["ibge6", "ano"]).tail(1)
ult.to_csv(OUT / "mm_serie.csv", index=False)
print("✓", len(ult))
