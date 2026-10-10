"""Bolsa Família por município, mês a mês (MDS, MI Social), desde o relançamento do programa (03/2023).

Saída: raw/mds/bf_mensal.csv (codigo_ibge 6 dígitos, anomes, famílias, pessoas, valor pago no mês).
Uso: python scripts/06_bolsa_familia.py
"""
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "raw" / "mds" / "bf_mensal.csv"
MDS = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"
CAMPOS = "codigo_ibge,anomes_s,qtd_familias_beneficiarias_bolsa_familia_i,qtd_pessoas_beneficiarias_bolsa_familia_i,valor_repassado_bolsa_familia_f"

partes = []
for mes in pd.period_range("2023-03", pd.Timestamp.today().to_period("M"), freq="M"):
    m = mes.strftime("%Y%m")
    r = requests.get(MDS, params={"q": "*:*", "fq": f"anomes_s:{m}", "fl": CAMPOS, "rows": 10000, "wt": "csv"}, timeout=120)
    r.raise_for_status()
    from io import StringIO
    d = pd.read_csv(StringIO(r.text), dtype={"codigo_ibge": str, "anomes_s": str})
    n = d.valor_repassado_bolsa_familia_f.notna().sum()
    print(m, len(d), "com valor:", n)
    if n > 5000:
        partes.append(d)
OUT.parent.mkdir(parents=True, exist_ok=True)
pd.concat(partes).to_csv(OUT, index=False)
print("✓", OUT)
