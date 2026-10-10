"""Agrega a votação de PRESIDENTE por local de votação (2T22 e 1T26), a partir dos arquivos por seção do TSE.

Baixa (se faltar) para raw/tse/secao/:
  votacao_secao_{2022,2026}_BR.zip        votos por seção e votável (só presidente)
  detalhe_votacao_secao_{2022,2026}.zip   aptos, comparecimento e abstenção por seção
  eleitorado_local_votacao_2026.zip       nome, endereço, bairro e coordenadas dos locais (em raw/tse/)
Saída: raw/derivados/locais.pkl (uma linha por local de votação de 2026, com o 2T22 do mesmo local quando comparável)

Uso: python scripts/05_secoes.py
"""
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
SEC = RAW / "tse" / "secao"
OUT = RAW / "derivados"
SEC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
KEY = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO"]
LULA, ADV, BRANCO, NULO = 13, 22, 95, 96


def baixa(url, dest):
    if dest.exists():
        return dest
    print("↓", url)
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(".part")
        with open(tmp, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    tmp.rename(dest)
    return dest


def votos(ano, turno, candidatos):
    z = baixa(f"{CDN}/votacao_secao/votacao_secao_{ano}_BR.zip", SEC / f"votacao_secao_{ano}_BR.zip")
    out = []
    with zipfile.ZipFile(z) as zf:
        nome = next(n for n in zf.namelist() if n.endswith(".csv"))
        for ch in pd.read_csv(zf.open(nome), sep=";", encoding="latin1", chunksize=2_000_000, dtype={"CD_MUNICIPIO": str},
                              usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_VOTAVEL", "QT_VOTOS",
                                       "NR_LOCAL_VOTACAO"]):
            ch = ch[ch.NR_TURNO == turno]
            # votável fora da lista de candidatos (ex.: nulo técnico) conta como branco/nulo
            ch["k"] = np.select([ch.NR_VOTAVEL == LULA, ch.NR_VOTAVEL == ADV, ch.NR_VOTAVEL.isin(candidatos)],
                                ["lula", "adv", "outros"], "bn")
            out.append(ch.groupby(KEY + ["k"]).QT_VOTOS.sum())
    v = pd.concat(out).groupby(level=list(range(5))).sum().unstack(fill_value=0)
    for c in ["lula", "adv", "outros", "bn"]:
        if c not in v:
            v[c] = 0
    return v


def detalhe(ano, turno):
    z = baixa(f"{CDN}/detalhe_votacao_secao/detalhe_votacao_secao_{ano}.zip", SEC / f"detalhe_votacao_secao_{ano}.zip")
    out = []
    with zipfile.ZipFile(z) as zf:
        for nome in zf.namelist():
            if not nome.endswith(".csv") or "BRASIL" in nome:
                continue
            for ch in pd.read_csv(zf.open(nome), sep=";", encoding="latin1", chunksize=2_000_000, dtype={"CD_MUNICIPIO": str},
                                  usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "CD_CARGO", "QT_APTOS",
                                           "QT_ABSTENCOES", "NR_LOCAL_VOTACAO"]):
                ch = ch[(ch.NR_TURNO == turno) & (ch.CD_CARGO == 1)]
                out.append(ch.groupby(KEY)[["QT_APTOS", "QT_ABSTENCOES"]].sum())
    d = pd.concat(out).groupby(level=list(range(4))).sum()
    d.columns = ["aptos", "abst"]
    return d


def norm_key(df):
    df = df.reset_index()
    df["CD_MUNICIPIO"] = df.CD_MUNICIPIO.str.zfill(5)
    return df.set_index(KEY)


cand26 = pd.read_csv(RAW / "tse" / "votacao_candidato_munzona_2026_BR.csv", sep=";", encoding="latin1",
                     usecols=["NR_CANDIDATO"]).NR_CANDIDATO.unique().tolist()
v26 = norm_key(votos(2026, 1, cand26))
v22 = norm_key(votos(2022, 2, [LULA, ADV]))
d26 = norm_key(detalhe(2026, 1))
d22a = norm_key(detalhe(2022, 1))
d22b = norm_key(detalhe(2022, 2))

L = d26.join(v26, how="outer").fillna(0)
L = L.add_suffix("_26")
p22 = d22b.join(v22, how="outer").fillna(0)[["aptos", "abst", "lula", "adv", "bn"]].add_suffix("_22")
h = d22a.add(d22b, fill_value=0).add_suffix("_h")  # abstenção histórica = 1T22 + 2T22
L = L.join(p22, how="left").join(h, how="left")
# o mesmo número de local só é comparável se o eleitorado não mudou demais (0,5x a 2x)
r = L.aptos_26.astype(float) / L.aptos_22.astype(float).replace(0, np.nan)
L["comparavel"] = L.aptos_22.notna() & (r > 0.5) & (r < 2)

# cadastro de locais 2026: nome, endereço, bairro, coordenadas
cad = []
with zipfile.ZipFile(RAW / "tse" / "eleitorado_local_votacao_2026.zip") as zf:
    for nome in zf.namelist():
        if nome.endswith(".csv") and "BRASIL" not in nome:
            d = pd.read_csv(zf.open(nome), sep=";", encoding="latin1", dtype={"CD_MUNICIPIO": str},
                            usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO",
                                     "DS_ENDERECO", "NM_BAIRRO", "NR_LATITUDE", "NR_LONGITUDE"])
            cad.append(d[d.NR_TURNO == 1].drop(columns="NR_TURNO"))
cad = pd.concat(cad)
cad["CD_MUNICIPIO"] = cad.CD_MUNICIPIO.str.zfill(5)
cad = cad.drop_duplicates(KEY).set_index(KEY)
L = L.join(cad, how="left").reset_index()
L = L[L.SG_UF != "ZZ"]
L.to_pickle(OUT / "locais.pkl")
print(f"locais {len(L)} | comparáveis {L.comparavel.mean():.1%} dos locais, "
      f"{L[L.comparavel].lula_26.sum() / L.lula_26.sum():.1%} dos votos de Lula 1T26 | sem cadastro {L.NM_BAIRRO.isna().sum()}")
print({k: int(L[k].sum()) for k in ["aptos_26", "abst_26", "lula_26", "adv_26", "outros_26", "bn_26", "lula_22", "adv_22"]})
