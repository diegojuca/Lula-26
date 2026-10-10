"""Entregas federais por município (além do Bolsa Família, que vem do 06_bolsa_familia.py).

- Pé-de-Meia (MEC), via download em massa do Portal da Transparência (CGU): estudantes com pagamento
  e valor pago no último mês publicado (parcelas pagas). Só as colunas de município e valor são lidas;
  o arquivo bruto (que tem dados pessoais) é APAGADO após a agregação.
- Mais Médicos (Ministério da Saúde, API de Dados Abertos): médicos ativos no programa por município.
- Tabela de municípios do SIAFI x IBGE (Tesouro Transparente), para casar o código do Portal.

Saída: raw/federal/federal_municipios.csv e raw/federal/federal_meta.json
Uso: python scripts/07_federal.py
"""
import io
import json
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "raw" / "federal"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (painel-cenario-2026; dados abertos)"}
CGU = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/pe-de-meia/{m}_PeDeMeia.zip"
TABMUN = ("https://www.tesourotransparente.gov.br/ckan/dataset/abb968cb-3710-4f85-89cf-875c91b9c7f6/resource/"
          "eebb3bc6-9eea-4496-8bcf-304f33155282/download/tabmun.csv")
SAUDE = "https://apidadosabertos.saude.gov.br/atencao-primaria/pmmb-consolidado"


def get(url, **kw):
    for i in range(5):
        try:
            r = requests.get(url, headers=UA, timeout=kw.pop("timeout", 120), **kw)
            return r
        except requests.RequestException as e:
            if i == 4:
                raise
            print("  retry", e)
            time.sleep(2 ** i)


# ---------------------------------------------------------------- SIAFI x IBGE
tab = pd.read_csv(io.StringIO(get(TABMUN).content.decode("latin1")), sep=";", header=None, dtype=str,
                  names=["siafi", "cnpj", "nome", "uf", "ibge"])
siafi2ibge = dict(zip(tab.siafi.str.strip(), tab.ibge.str.strip()))

# ---------------------------------------------------------------- Pé-de-Meia: último mês publicado
mes = pd.Timestamp.today().to_period("M")
for _ in range(12):
    m = mes.strftime("%Y%m")
    if get(CGU.format(m=m), stream=True).status_code == 200:
        break
    mes -= 1
zpath = OUT / f"pdm_{m}.zip"
if not zpath.exists():
    print("↓ Pé-de-Meia", m)
    with get(CGU.format(m=m), stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(zpath, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
partes = []
with zipfile.ZipFile(zpath) as zf:
    nome = zf.namelist()[0]
    # só código do município e valor: nenhuma coluna pessoal é lida. Pagamentos a menores de 18 anos vêm
    # anonimizados no Portal, então não há como contar estudantes distintos: a medida é o número de parcelas pagas.
    for ch in pd.read_csv(zf.open(nome), sep=";", encoding="latin1", usecols=["CÓDIGO MUNICÍPIO SIAFI", "VALOR PARCELA"],
                          dtype=str, chunksize=2_000_000):
        ch["v"] = pd.to_numeric(ch["VALOR PARCELA"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
        partes.append(ch[["CÓDIGO MUNICÍPIO SIAFI", "v"]])
pdm = pd.concat(partes)
partes = None
pdm["ibge"] = pdm["CÓDIGO MUNICÍPIO SIAFI"].str.strip().map(siafi2ibge)
sem = pdm.ibge.isna().mean()
agg = pdm.groupby("ibge").agg(pdm_parcelas=("v", "size"), pdm_valor=("v", "sum"))
tot_parc, tot_valor = int(len(pdm)), float(pdm.v.sum())
del pdm
zpath.unlink()  # remove o arquivo com dados pessoais
print(f"✓ Pé-de-Meia {m}: {tot_parc:,} parcelas, R$ {tot_valor:,.2f} | sem município IBGE: {sem:.3%}")

# ---------------------------------------------------------------- Mais Médicos
linhas, off = [], 0
while True:
    r = get(SAUDE, params={"limit": 1000, "offset": off})
    r.raise_for_status()
    js = r.json().get("pmmb", [])
    if not js:
        break
    linhas += js
    off += len(js)
mm = pd.DataFrame(linhas)
mm = mm[mm.nivel.str.upper().str.startswith("MUN")].copy()
mm["cod6"] = mm.co_ibge.astype(int).astype(str).str.zfill(6)
cod7 = {i[:6]: i for i in tab.ibge.str.strip()}
mm["ibge"] = mm.cod6.map(cod7)
mm_ref = str(mm.dt_referencia.dropna().max())
mmagg = mm.groupby("ibge").agg(mm_medicos=("total_ocupadas", "sum"))
print(f"✓ Mais Médicos ({mm_ref}): {len(mm)} municípios, {int(mmagg.mm_medicos.sum()):,} vagas ocupadas; níveis: {sorted(set(pd.DataFrame(linhas).nivel))}")

fed = agg.join(mmagg, how="outer")
fed.index.name = "ibge"
fed.reset_index().to_csv(OUT / "federal_municipios.csv", index=False)
(OUT / "federal_meta.json").write_text(json.dumps({
    "pdm_mes": m, "pdm_parcelas": tot_parc, "pdm_valor": tot_valor,
    "mm_referencia": mm_ref, "mm_total": int(mmagg.mm_medicos.sum()),
}, ensure_ascii=False))
print("✓", OUT / "federal_municipios.csv")
