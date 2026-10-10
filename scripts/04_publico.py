"""Gera a versão PÚBLICA (militância) a partir da mesma base da análise.

Entradas: data/municipios.json, data/meta.json, data/geo_municipios.json (02_build.py)
          raw/derivados/locais.pkl (05_secoes.py) e raw/mds/bf_mensal.csv (06_bolsa_familia.py)
Saídas:   painel_publico/index.html   página com o índice de cidades embutido
          painel_publico/dados/<UF>.json (e <id>.json das maiores cidades), carregados sob demanda:
          locais de votação, bairros, perfil da cidade e Bolsa Família
          data_publico/checagem.json  números usados na conferência

A versão pública não traz religião, raça/cor, fórmulas nem termos técnicos.
Uso: python scripts/04_publico.py
"""
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"
PUB = ROOT / "painel_publico"
DADOS = PUB / "dados"
OUTD = ROOT / "data_publico"
for d in (DADOS, OUTD):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- parâmetros
ACAO = {"mobilizacao": 1, "reconquista": 2, "disputa": 3}  # 1 levar p/ votar, 2 conversar, 3 bairro a bairro
CIDADE_GRANDE = 200_000     # eleitores: acima disso, a página agrupa os locais por bairro
AMOSTRA_PEQUENA = 300       # locais com menos eleitores: sem percentuais nem ação
ARQ_PROPRIO = 1000          # cidades com mais locais que isso ganham arquivo próprio
PORTES = [10_000, 50_000, 200_000, 1_000_000]  # limites das faixas de porte (eleitores 1T26)
REG = {"reduto": 55.0, "adverso": 45.0, "queda": -7.0, "abst_alta": 25.0, "abst_cresc": 2.0}  # mesmas regras da análise


def tab(path):
    j = json.loads(path.read_text())
    return pd.DataFrame(j["rows"], columns=j["cols"])


mun = tab(DATA / "municipios.json")
meta = json.loads((DATA / "meta.json").read_text())
geo = json.loads((DATA / "geo_municipios.json").read_text())
ibge_nome = {str(m["id"]): m["nome"] for m in json.loads((RAW / "ibge" / "municipios.json").read_text())}
cm = json.loads((RAW / "tse_resultados" / "mun-cm.json").read_text())
tse2ibge = {m["cd"]: m["cdi"] for a in cm["abr"] for m in a["mu"] if m.get("cdi")}
AMC = {m: meta["amc"]["membros"][0] for m in meta["amc"]["membros"][1:]}

MINUSC = {"de", "da", "do", "das", "dos", "e", "a", "o"}
SIGLAS = {"ee", "emef", "emei", "cei", "ceu", "ufba", "ufpe", "ufrj", "usp", "unb", "senai", "sesi", "senac", "sesc",
          "cmei", "ciep", "caic", "ifba", "ifsp", "eeef", "emeif", "eef", "eem", "eeefm", "ii", "iii", "iv", "jk"}


def titulo(s):
    if not isinstance(s, str) or not s.strip():
        return ""
    s = re.sub(r"\b([a-z]{1,5})\.(?=[a-z])", r"\1. ", s.strip().lower())  # "ee.carlos" -> "ee. carlos"
    w = re.sub(r"\s+", " ", s).split(" ")
    out = []
    for k, x in enumerate(w):
        if x.strip(".-") in SIGLAS:
            out.append(x.upper())
        elif x in MINUSC and k:
            out.append(x)
        else:
            out.append(x[:1].upper() + x[1:])
    return " ".join(out)


def porte(a):
    return int(np.searchsorted(PORTES, a, side="right"))


# ---------------------------------------------------------------- locais de votação
L = pd.read_pickle(RAW / "derivados" / "locais.pkl")
L["id"] = L.CD_MUNICIPIO.map(tse2ibge).map(lambda i: AMC.get(i, i))
assert L.id.notna().all()
L = L.merge(mun[["id", "abs_hist"]], on="id", how="left")
num = ["aptos_26", "abst_26", "lula_26", "adv_26", "outros_26", "bn_26", "aptos_22", "abst_22", "lula_22", "adv_22",
       "aptos_h", "abst_h"]
L[num] = L[num].astype(float)
# 2022 só entra quando o local é comparável
for c in ["aptos_22", "abst_22", "lula_22", "adv_22", "aptos_h", "abst_h"]:
    L.loc[~L.comparavel, c] = np.nan


def metricas(d, abs_hist_padrao):
    v26 = d.lula_26 + d.adv_26 + d.outros_26
    d["pv22"] = 100 * d.lula_22 / (d.lula_22 + d.adv_22)
    d["pv26"] = 100 * d.lula_26 / v26
    d["pen22"] = 100 * d.lula_22 / d.aptos_22
    d["pen26c"] = 100 * d.lula_26c / d.aptos_26c
    d["dpen"] = d.pen26c - d.pen22
    d["abs26"] = 100 * d.abst_26 / d.aptos_26
    hist = 100 * d.abst_h / d.aptos_h
    d["abs_h"] = hist.where(hist.notna(), abs_hist_padrao)
    d["exc"] = ((d.abs26 - d.abs_h).clip(lower=0) / 100 * d.aptos_26).fillna(0)
    d["jogo"] = d.outros_26 + d.bn_26 + d.exc
    d["pot"] = (-d.dpen).clip(lower=0).fillna(0) / 100 * d.aptos_26 + d.exc * d.pv22.fillna(d.pv26) / 100
    red = d.pv22 >= REG["reduto"]
    d["acao"] = np.select(
        [red & (d.dpen <= REG["queda"]),
         red & ((d.abs26 >= REG["abst_alta"]) | (d.abs26 - d.abs_h >= REG["abst_cresc"])),
         (d.pv22 >= REG["adverso"]) & (d.pv22 < REG["reduto"])], [2, 1, 3], 0)
    d.loc[d.pv22.isna() | (d.aptos_26 < AMOSTRA_PEQUENA), "acao"] = 0
    return d


# variáveis "c" = 1T26 só nos locais comparáveis (para a variação usar a mesma base)
L["lula_26c"] = L.lula_26.where(L.comparavel)
L["aptos_26c"] = L.aptos_26.where(L.comparavel)
L = metricas(L, L.abs_hist)
L["bairro"] = L.NM_BAIRRO.map(titulo)
L["nome"] = L.NM_LOCAL_VOTACAO.map(titulo)
L["end"] = L.DS_ENDERECO.map(titulo)
L.loc[L.nome == "", "nome"] = "Local " + L.NR_LOCAL_VOTACAO.astype(str) + " (zona " + L.NR_ZONA.astype(str) + ")"

# ---------------------------------------------------------------- coordenadas (cadastro do TSE)
num_br = lambda s: pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")
L["lat"], L["lon"] = num_br(L.NR_LATITUDE), num_br(L.NR_LONGITUDE)
okc = L.lat.between(-34, 6) & L.lon.between(-75, -28) & (L.lat != -1)
L.loc[~okc, ["lat", "lon"]] = np.nan
L["aprox"] = ~okc
# sem coordenada: ponto médio dos locais do mesmo bairro; senão, ponto médio dos locais do município; senão, centro do município
for chave in (["id", "bairro"], ["id"]):
    med = L.groupby(chave)[["lat", "lon"]].transform("mean")
    L["lat"] = L.lat.fillna(med.lat)
    L["lon"] = L.lon.fillna(med.lon)

cent = {}  # centro aproximado do município (caixa do maior polígono), último recurso
for f in geo["features"]:
    i = f["properties"]["id"]
    polys = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]
    ring = max((p[0] for p in polys), key=len)
    xs, ys = [c[0] for c in ring], [c[1] for c in ring]
    cent.setdefault(i, (round((min(xs) + max(xs)) / 2, 4), round((min(ys) + max(ys)) / 2, 4)))
L["lat"] = L.lat.fillna(L.id.map(lambda i: cent.get(i, (np.nan, np.nan))[1]))
L["lon"] = L.lon.fillna(L.id.map(lambda i: cent.get(i, (np.nan, np.nan))[0]))
print(f"coordenadas: {okc.mean():.1%} dos locais com ponto do TSE; demais com posição aproximada")
# ponto da bolha do município: média dos locais ponderada pelo eleitorado (onde as pessoas votam)
_w = L.aptos_26.clip(lower=1)
ponto_mun = (L.assign(wl=L.lat * _w, wo=L.lon * _w, w=_w).groupby("id")[["wl", "wo", "w"]].sum())
ponto_mun = {i: (round(r.wo / r.w, 3), round(r.wl / r.w, 3)) for i, r in ponto_mun.iterrows()}

# conferência: soma dos locais = município da análise
chk = L.groupby("id")[["aptos_26", "lula_26", "adv_26"]].sum().join(mun.set_index("id")[["aptos_26", "lula_26", "adv_26"]], rsuffix="_a")
dif = chk[(chk.aptos_26 != chk.aptos_26_a) | (chk.lula_26 != chk.lula_26_a) | (chk.adv_26 != chk.adv_26_a)]
assert dif.empty, f"Locais não somam o município em {len(dif)} cidades:\n{dif.head()}"
print(f"✓ soma dos locais = município em todas as {len(chk)} cidades (aptos, Lula e adversário 1T26)")

# ---------------------------------------------------------------- Bolsa Família
bf = pd.read_csv(RAW / "mds" / "bf_mensal.csv", dtype={"codigo_ibge": str, "anomes_s": str})
cod7 = {k[:6]: k for k in ibge_nome}
bf["id"] = bf.codigo_ibge.map(cod7).map(lambda i: AMC.get(i, i))
ULT = bf.anomes_s.max()
PRI = bf.anomes_s.min()
bf_ult = bf[bf.anomes_s == ULT].groupby("id")[["qtd_familias_beneficiarias_bolsa_familia_i",
                                                 "qtd_pessoas_beneficiarias_bolsa_familia_i",
                                                 "valor_repassado_bolsa_familia_f"]].sum()
bf_acum = bf.groupby("id").valor_repassado_bolsa_familia_f.sum()

# Pé-de-Meia e Mais Médicos (07_federal.py)
fed = pd.read_csv(RAW / "federal" / "federal_municipios.csv", dtype={"ibge": str})
fed["id"] = fed.ibge.map(lambda i: AMC.get(i, i))
fed = fed.groupby("id")[["pdm_parcelas", "pdm_valor", "mm_medicos"]].sum(min_count=1)
fed_meta = json.loads((RAW / "federal" / "federal_meta.json").read_text())

# ---------------------------------------------------------------- perfil da cidade (sem religião e sem raça/cor)
PERFIL = ["pop", "renda_media", "pbf_pop", "urbana", "el_jov", "el_ido", "el_baixa", "el_sup"]
media_uf = {}
for uf, g in mun.groupby("uf"):
    w = g["pop"]
    we = g.aptos_26
    media_uf[uf] = {
        "renda_media": round(float(np.average(g.renda_media, weights=w)), 0),
        "pbf_pop": round(float(np.average(g.pbf_pop, weights=w)), 1),
        "urbana": round(float(np.average(g.urbana, weights=w)), 1),
        "el_jov": round(float(np.average(g.el_jov, weights=we)), 1),
        "el_ido": round(float(np.average(g.el_ido, weights=we)), 1),
        "el_baixa": round(float(np.average(g.el_baixa, weights=we)), 1),
        "el_sup": round(float(np.average(g.el_sup, weights=we)), 1),
    }


def r1(v):
    return None if v is None or (isinstance(v, float) and not np.isfinite(v)) else round(float(v), 1)


def r10(v):  # percentual * 10, inteiro (economiza bytes); -1 = sem dado
    return -1 if v is None or not np.isfinite(v) else int(round(v * 10))


# ---------------------------------------------------------------- arquivos sob demanda
nloc = L.groupby("id").size()
arquivo = {i: (i if nloc.get(i, 0) > ARQ_PROPRIO else uf) for i, uf in zip(mun.id, mun.uf)}
pacotes = {}
SOMA = ["aptos_26", "abst_26", "lula_26", "adv_26", "outros_26", "bn_26", "aptos_22", "abst_22", "lula_22", "adv_22",
        "aptos_h", "abst_h", "lula_26c", "aptos_26c"]
mun_i = mun.set_index("id")
checagem = {}
for i, g in L.groupby("id"):
    m = mun_i.loc[i]
    g = g.sort_values("pot", ascending=False)
    grande = m.aptos_26 >= CIDADE_GRANDE
    bairros = []
    bidx = {}
    if grande:
        b = g.groupby("bairro")[SOMA].sum(min_count=1)
        b = metricas(b, m.abs_hist).sort_values("pot", ascending=False)
        for k, (nome, r) in enumerate(b.iterrows()):
            bidx[nome] = k
            gb = g[g.bairro == nome]
            wb = gb.aptos_26.clip(lower=1)
            bairros.append([nome or "Sem bairro", int(gb.shape[0]), int(r.aptos_26), r10(r.pv22),
                            r10(r.pv26), r10(r.abs26), int(round(r.jogo)), int(r.acao),
                            round(float((gb.lat * wb).sum() / wb.sum()), 4), round(float((gb.lon * wb).sum() / wb.sum()), 4)])
    locais = []
    for r in g.itertuples():
        peq = r.aptos_26 < AMOSTRA_PEQUENA
        novo = not r.comparavel
        locais.append([r.nome, r.end, bidx.get(r.bairro, r.bairro) if grande else r.bairro, int(r.aptos_26),
                       -1 if peq else r10(r.pv22), -1 if peq else r10(r.pv26), -1 if peq else r10(r.abs26),
                       int(round(r.jogo)), int(r.acao), (1 if peq else 0) | (2 if novo else 0) | (4 if r.aprox else 0),
                       round(float(r.lat), 4), round(float(r.lon), 4)])
    fam = bf_ult.loc[i] if i in bf_ult.index else None
    perfil = {k: r1(m[k]) for k in PERFIL}
    perfil["pop"] = int(m["pop"]) if np.isfinite(m["pop"]) else None
    perfil["renda_media"] = int(round(m.renda_media)) if np.isfinite(m.renda_media) else None
    pac = {"perfil": perfil,
           "bf": None if fam is None else {
               "familias": int(fam.qtd_familias_beneficiarias_bolsa_familia_i),
               "pessoas": int(fam.qtd_pessoas_beneficiarias_bolsa_familia_i),
               "valor_mes": float(fam.valor_repassado_bolsa_familia_f),
               "valor_acum": float(bf_acum.loc[i])},
           "fed": None if i not in fed.index else {
               "pdm_parcelas": None if pd.isna(fed.loc[i, "pdm_parcelas"]) else int(fed.loc[i, "pdm_parcelas"]),
               "pdm_valor": None if pd.isna(fed.loc[i, "pdm_valor"]) else float(fed.loc[i, "pdm_valor"]),
               "mm_medicos": None if pd.isna(fed.loc[i, "mm_medicos"]) else int(fed.loc[i, "mm_medicos"])},
           "grande": bool(grande), "bairros": bairros, "locais": locais}
    pacotes.setdefault(arquivo[i], {})[i] = pac
    checagem[i] = {"locais": g.head(2)[["NR_ZONA", "NR_LOCAL_VOTACAO", "nome", "aptos_26", "abst_26", "lula_26",
                                        "adv_26", "lula_22", "adv_22"]].to_dict(orient="records"),
                   "bf": pac["bf"], "fed": pac["fed"]}

# divide UFs grandes em partes de até ~MAX_ARQ bytes (carregamento rápido no 4G)
MAX_ARQ = 500_000
for k in [k for k in list(pacotes) if not k.isdigit()]:
    tam = {i: len(json.dumps(v, ensure_ascii=False, separators=(",", ":")).encode()) for i, v in pacotes[k].items()}
    if sum(tam.values()) <= MAX_ARQ:
        continue
    partes, atual, soma = [], {}, 0
    for i in sorted(pacotes[k]):
        if atual and soma + tam[i] > MAX_ARQ:
            partes.append(atual)
            atual, soma = {}, 0
        atual[i] = pacotes[k][i]
        soma += tam[i]
    partes.append(atual)
    del pacotes[k]
    for n, parte in enumerate(partes, 1):
        pacotes[f"{k}-{n}"] = parte
        for i in parte:
            arquivo[i] = f"{k}-{n}"

for f in DADOS.glob("*.json"):
    f.unlink()
tamanhos = {}
for k, v in pacotes.items():
    p = DADOS / f"{k}.json"
    p.write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")))
    tamanhos[k] = p.stat().st_size
(OUTD / "checagem.json").write_text(json.dumps(checagem, ensure_ascii=False, default=float))

# ---------------------------------------------------------------- índice (embutido na página)

idx = []
for r in mun.itertuples():
    lon, lat = ponto_mun.get(r.id, cent.get(r.id, (None, None)))
    row = [r.id, r.nome, r.uf, ACAO.get(r.seg, 0), int(round(r.estoque)), lon, lat, porte(r.aptos_26),
           r10(r.pv_l22), r10(r.pv_l26), int(r.d_lula), arquivo[r.id] if arquivo[r.id] != r.uf else 0]
    idx.append(row)
    if r.id in AMC.values():
        for alias, dest in AMC.items():
            if dest == r.id:
                idx.append([r.id, ibge_nome[alias]] + row[2:])
idx.sort(key=lambda x: unicodedata.normalize("NFKD", x[1]).encode("ascii", "ignore").decode().lower())

# destaque: cidades pequenas (até 50 mil eleitores)
peq = mun.aptos_26 < 50_000
tot = mun.d_saldo.sum()
B = meta["brasil"]
pub = {
    "deficit": int(B["deficit"]), "jogo": int(meta["brasil_sem_exterior"]["estoque"]),
    "pequenas": {"n": int(peq.sum()), "saldo": int(mun[peq].d_saldo.sum()), "saldo_total": int(tot),
                 "parte": round(100 * mun[peq].d_saldo.sum() / tot), "pv22": r1(100 * mun[peq].lula_22.sum() / mun[peq].validos_22.sum()),
                 "pv26": r1(100 * mun[peq].lula_26.sum() / mun[peq].validos_26.sum())},
    "gerado_1t26": meta["fontes"][1]["gerado"], "extracao": meta["data_extracao"],
    "bf_periodo": [PRI, ULT], "pdm_mes": fed_meta["pdm_mes"], "mm_ref": fed_meta["mm_referencia"], "media_uf": media_uf, "portes": PORTES,
    "cidades": idx,
}
# ---------------------------------------------------------------- mapa: contornos (IBGE) simplificados e bolhas por UF
MAPA = PUB / "mapa"
MAPA.mkdir(exist_ok=True)


def rdp(pts, tol):
    """Douglas-Peucker iterativo (graus)."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        a, b = pilha.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n2 = dx * dx + dy * dy or 1e-18
        dm, im = -1, -1
        for k in range(a + 1, b):
            x, y = pts[k]
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / n2))
            d = (x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2
            if d > dm:
                dm, im = d, k
        if dm > tol * tol:
            keep[im] = True
            pilha += [(a, im), (im, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplifica(feats, tol, nd):
    out = []
    for f in feats:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        novos = []
        for poly in polys:
            aneis = [[[round(x, nd), round(y, nd)] for x, y in rdp(ring, tol)] for ring in poly[:1]]  # só o anel externo
            if len(aneis[0]) >= 4:
                novos.append(aneis)
        if novos:
            out.append({"type": "Feature", "properties": f["properties"],
                        "geometry": {"type": "MultiPolygon", "coordinates": novos}})
    return {"type": "FeatureCollection", "features": out}


geo_ufs = json.loads((DATA / "geo_ufs.json").read_text())
(MAPA / "ufs.json").write_text(json.dumps(simplifica(geo_ufs["features"], 0.02, 2), separators=(",", ":")))
UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
         "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
         "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
por_uf = {}
for f in geo["features"]:
    por_uf.setdefault(UFCOD[f["properties"]["id"][:2]], []).append(f)
tam_mapa = {}
for uf, fs in por_uf.items():
    p = MAPA / f"mun_{uf}.json"
    p.write_text(json.dumps(simplifica(fs, 0.012, 3), separators=(",", ":")))
    tam_mapa[uf] = p.stat().st_size


def centroide(feat):
    polys = feat["geometry"]["coordinates"] if feat["geometry"]["type"] == "MultiPolygon" else [feat["geometry"]["coordinates"]]
    r = max((p[0] for p in polys), key=len)
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(r, r[1:]):
        c = x1 * y2 - x2 * y1
        a += c
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    return round(cx / (3 * a), 2), round(cy / (3 * a), 2)


uf_tab = pd.DataFrame(json.loads((DATA / "ufs.json").read_text())["rows"], columns=json.loads((DATA / "ufs.json").read_text())["cols"]).set_index("uf")
ufs_mapa = {}
for f in geo_ufs["features"]:
    uf = f["properties"]["id"]
    lon, lat = centroide(f)
    prio = mun[(mun.uf == uf) & mun.seg.isin(ACAO)]
    ufs_mapa[uf] = [int(round(uf_tab.loc[uf, "estoque"])), lon, lat, int(len(prio)), int(round(prio.estoque.sum()))]
pub["ufs"] = ufs_mapa
print(f"mapa: ufs.json {(MAPA / 'ufs.json').stat().st_size / 1e3:.0f} KB | contornos municipais por UF: maior "
      f"{max(tam_mapa, key=tam_mapa.get)} {max(tam_mapa.values()) / 1e3:.0f} KB, total {sum(tam_mapa.values()) / 1e6:.1f} MB")

tpl = (PUB / "template.html").read_text()
html = tpl.replace("/*__DADOS__*/null", json.dumps(pub, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
(PUB / "index.html").write_text(html)

print(f"index.html {len(html.encode()) / 1e3:.0f} KB | arquivos sob demanda: {len(tamanhos)}, "
      f"total {sum(tamanhos.values()) / 1e6:.1f} MB, maior {max(tamanhos, key=tamanhos.get)} {max(tamanhos.values()) / 1e3:.0f} KB")
print("pequenas:", pub["pequenas"], "| BF", PRI, "→", ULT)
print("locais por ação:", L.acao.value_counts().to_dict())
