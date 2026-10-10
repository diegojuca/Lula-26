"""Séries históricas municipais para os cards (MDS MI Social): Bolsa Família / Auxílio Brasil e cisternas.

Bolsa Família (até out/2021 e de mar/2023 em diante): famílias e valor repassado.
Auxílio Brasil (nov/2021–fev/2023): famílias e valor pago = benefício regular + benefício extraordinário
(sem o extraordinário, o período ficaria subestimado).
Saída: raw/series/mds_mensal.csv
Uso: python scripts/08_series.py
"""
import io
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "raw" / "series" / "mds_mensal.csv"
MDS = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"
CAMPOS = ("codigo_ibge,anomes_s,qtd_familias_beneficiarias_bolsa_familia_i,valor_repassado_bolsa_familia_f,"
          "pab_qtd_fam_benef_i,pab_valor_pago_d,pab_extraordinario_valor_pago_d,qtd_cisternas_entregues_total_mds_i")
partes = []
for mes in pd.period_range("2004-01", pd.Timestamp.today().to_period("M"), freq="M"):
    m = mes.strftime("%Y%m")
    for t in range(5):
        try:
            r = requests.get(MDS, params={"q": "*:*", "fq": f"anomes_s:{m}", "fl": CAMPOS, "rows": 10000, "wt": "csv"}, timeout=120)
            r.raise_for_status()
            break
        except requests.RequestException:
            time.sleep(2 ** t)
    d = pd.read_csv(io.StringIO(r.text), dtype={"codigo_ibge": str, "anomes_s": str})
    if len(d):
        partes.append(d)
    if m.endswith("12"):
        print(m, len(d))
pd.concat(partes).to_csv(OUT, index=False)
print("✓", OUT)
