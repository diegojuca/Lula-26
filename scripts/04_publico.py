"""Gera os dados e a página da versão PÚBLICA (mobilização) a partir da mesma base da análise.

Entradas: data/municipios.json, data/meta.json, data/geo_municipios.json (saídas do 02_build.py)
          + raw/ (TSE por zona e locais de votação) só para o detalhamento por zona/bairro.
Saídas:   data_publico/publico.json e painel_publico/index.html (página única, dados embutidos).

A versão pública NÃO carrega indicadores socioeconômicos, fórmulas nem termos técnicos.
Uso: python scripts/04_publico.py   (rodar depois do 02_build.py)
"""
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"
OUT = ROOT / "data_publico"
OUT.mkdir(exist_ok=True)

# Segmento da análise -> ação da versão pública (os demais segmentos não aparecem com nome)
ACAO = {"mobilizacao": 1, "reconquista": 2, "disputa": 3}  # 1 levar p/ votar, 2 conversar, 3 bairro a bairro
CAPITAIS = {"1100205", "1200401", "1302603", "1400100", "1501402", "1600303", "1721000", "2111300", "2211001",
            "2304400", "2408102", "2507507", "2611606", "2704302", "2800308", "2927408", "3106200", "3205309",
            "3304557", "3550308", "4106902", "4205407", "4314902", "5002704", "5103403", "5208707", "5300108"}
ZONAS_POR_CIDADE = 8   # zonas exibidas por cidade (as de mais votos em jogo)
BAIRROS_POR_ZONA = 4


def tab(path):
    j = json.loads(path.read_text())
    return pd.DataFrame(j["rows"], columns=j["cols"])


mun = tab(DATA / "municipios.json")
meta = json.loads((DATA / "meta.json").read_text())
geo = json.loads((DATA / "geo_municipios.json").read_text())

# ---------------------------------------------------------------- centro aproximado de cada município (lon/lat)
cent = {}
for f in geo["features"]:
    i = f["properties"]["id"]
    polys = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]
    ring = max((p[0] for p in polys), key=len)
    xs, ys = [c[0] for c in ring], [c[1] for c in ring]
    if i not in cent:  # AMC: fica o primeiro polígono (Sorriso)
        cent[i] = (round((min(xs) + max(xs)) / 2, 2), round((min(ys) + max(ys)) / 2, 2))

# ---------------------------------------------------------------- zonas (cidades-alvo com mais de uma zona)
cm = json.loads((RAW / "tse_resultados" / "mun-cm.json").read_text())
tse2ibge = {m["cd"]: m["cdi"] for a in cm["abr"] for m in a["mu"] if m.get("cdi")}
alvo = set(mun[(mun.seg == "disputa") | mun.id.isin(CAPITAIS)].id)
alvo_tse = {t for t, i in tse2ibge.items() if i in alvo}


def det(ano):
    d = pd.read_csv(RAW / "tse" / f"detalhe_votacao_munzona_{ano}_BR.csv", sep=";", encoding="latin1",
                    dtype={"CD_MUNICIPIO": str})
    d["CD_MUNICIPIO"] = d.CD_MUNICIPIO.str.zfill(5)
    d = d[d.CD_MUNICIPIO.isin(alvo_tse)]
    d["bn"] = d.QT_VOTOS_BRANCOS + d.QT_TOTAL_VOTOS_NULOS
    return d.groupby(["NR_TURNO", "CD_MUNICIPIO", "NR_ZONA"])[["QT_APTOS", "QT_ABSTENCOES", "bn"]].sum()


d22, d26 = det(2022), det(2026)
c26 = pd.read_csv(RAW / "tse" / "votacao_candidato_munzona_2026_BR.csv", sep=";", encoding="latin1",
                  dtype={"CD_MUNICIPIO": str}, usecols=["CD_MUNICIPIO", "NR_ZONA", "NR_CANDIDATO", "QT_VOTOS_NOMINAIS_VALIDOS"])
c26["CD_MUNICIPIO"] = c26.CD_MUNICIPIO.str.zfill(5)
c26 = c26[c26.CD_MUNICIPIO.isin(alvo_tse) & ~c26.NR_CANDIDATO.isin([13, 22])]
outros = c26.groupby(["CD_MUNICIPIO", "NR_ZONA"]).QT_VOTOS_NOMINAIS_VALIDOS.sum()

z = d26.loc[1].copy()
z["outros"] = outros.reindex(z.index).fillna(0)
h = d22.loc[1].add(d22.loc[2], fill_value=0)
z = z.join(h.rename(columns={"QT_APTOS": "aptos_h", "QT_ABSTENCOES": "abst_h"})[["aptos_h", "abst_h"]], how="left")
z = z.reset_index()
z["id"] = z.CD_MUNICIPIO.map(tse2ibge)
abs_hist_mun = mun.set_index("id").abs_hist
# zona nova (sem 2022): usa a abstenção histórica do município
z["abs_h"] = np.where(z.aptos_h > 0, 100 * z.abst_h / z.aptos_h, z.id.map(abs_hist_mun))
z["abs26"] = 100 * z.QT_ABSTENCOES / z.QT_APTOS
z["exc"] = (z.abs26 - z.abs_h).clip(lower=0) / 100 * z.QT_APTOS
z["jogo"] = z.outros + z.bn + z.exc
nz = z.groupby("id").NR_ZONA.transform("count")
z = z[nz > 1]

# bairros de cada zona (locais de votação 2026, ponderados pelo eleitorado das seções)
loc = []
with zipfile.ZipFile(RAW / "tse" / "eleitorado_local_votacao_2026.zip") as zf:
    for n in zf.namelist():
        if n.endswith(".csv") and "BRASIL" not in n:
            d = pd.read_csv(zf.open(n), sep=";", encoding="latin1", dtype={"CD_MUNICIPIO": str},
                            usecols=["NR_TURNO", "CD_MUNICIPIO", "NR_ZONA", "NM_BAIRRO", "QT_ELEITOR_SECAO"])
            d["CD_MUNICIPIO"] = d.CD_MUNICIPIO.str.zfill(5)
            loc.append(d[(d.NR_TURNO == 1) & d.CD_MUNICIPIO.isin(alvo_tse)])
loc = pd.concat(loc)
loc["bairro"] = loc.NM_BAIRRO.fillna("").str.strip()
loc = loc[~loc.bairro.isin(["", "-", "#NULO", "NAO INFORMADO", "NÃO INFORMADO"])]
bz = loc.groupby(["CD_MUNICIPIO", "NR_ZONA", "bairro"]).QT_ELEITOR_SECAO.sum().reset_index()

MINUSC = {"de", "da", "do", "das", "dos", "e"}


def titulo(s):
    w = re.sub(r"\s+", " ", s.lower()).split(" ")
    return " ".join(x if (x in MINUSC and k) else x[:1].upper() + x[1:] for k, x in enumerate(w))


bairros = {}
for (m, zn), g in bz.groupby(["CD_MUNICIPIO", "NR_ZONA"]):
    bairros[(m, zn)] = [titulo(b) for b in g.sort_values("QT_ELEITOR_SECAO", ascending=False).bairro.head(BAIRROS_POR_ZONA)]

zonas = {}
for i, g in z.sort_values("jogo", ascending=False).groupby("id", sort=False):
    zonas[i] = [[int(r.NR_ZONA), int(round(r.jogo)), bairros.get((r.CD_MUNICIPIO, r.NR_ZONA), [])]
                for r in g.head(ZONAS_POR_CIDADE).itertuples()]

# ---------------------------------------------------------------- cidades
AMC_MEMBROS = meta["amc"]["membros"]
ibge_nome = {str(m["id"]): m["nome"] for m in json.loads((RAW / "ibge" / "municipios.json").read_text())}
cid = []
for r in mun.itertuples():
    lon, lat = cent.get(r.id, (None, None))
    cid.append([r.id, r.nome, r.uf, ACAO.get(r.seg, 0), int(round(r.estoque)), lon, lat])
    if r.id == AMC_MEMBROS[0]:  # municípios somados na área comparável: busca encontra cada nome
        for alias in AMC_MEMBROS[1:]:
            cid.append([r.id, ibge_nome[alias], r.uf, ACAO.get(r.seg, 0), int(round(r.estoque)), lon, lat])
cid.sort(key=lambda x: unicodedata.normalize("NFKD", x[1]).encode("ascii", "ignore").decode().lower())

B = meta["brasil"]
pub = {
    "deficit": int(B["deficit"]),
    "jogo": int(meta["brasil_sem_exterior"]["estoque"]),
    "gerado_1t26": meta["fontes"][1]["gerado"],
    "extracao": meta["data_extracao"],
    "cidades": cid,
    "zonas": zonas,
}
(OUT / "publico.json").write_text(json.dumps(pub, ensure_ascii=False, separators=(",", ":")))

tpl = (ROOT / "painel_publico" / "template.html").read_text()
payload = json.dumps(pub, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = tpl.replace("/*__DADOS__*/null", payload)
(ROOT / "painel_publico" / "index.html").write_text(html)

n_acao = pd.Series([c[3] for c in cid]).value_counts().to_dict()
print(f"cidades {len(cid)} | por ação {n_acao} | cidades com zonas {len(zonas)} ({sum(map(len, zonas.values()))} zonas)")
print(f"publico.json {(OUT / 'publico.json').stat().st_size / 1e3:.0f} KB | index.html {len(html.encode()) / 1e3:.0f} KB")
