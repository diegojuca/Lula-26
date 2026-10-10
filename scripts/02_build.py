"""Agrega os brutos de raw/ em JSON pré-agregados para o painel (data/).

Eixo analítico: 2º turno 2022 (2T22) -> 1º turno 2026 (1T26).
O 1T22 entra só como base da "abstenção histórica" (média de abstenção 1T22 e 2T22).

Uso: python scripts/02_build.py
"""
import json
import math
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

LULA = 13
ADV = 22  # 2T22: Jair Bolsonaro (PL) | 1T26: Flávio Bolsonaro (PL) — mesmo número/partido

REGIAO = {**dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Norte"),
          **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
          **dict.fromkeys(["DF", "GO", "MS", "MT"], "Centro-Oeste"),
          **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
          **dict.fromkeys(["PR", "RS", "SC"], "Sul"), "ZZ": "Exterior"}

# ---------------------------------------------------------------- parâmetros da segmentação
# Todos aparecem no painel (aba "Regras") — mudar aqui muda lá.
P = {
    "reduto_pv": 55.0,          # Lula >= 55% dos válidos no 2T22 = reduto
    "adverso_pv": 45.0,         # Lula < 45% dos válidos no 2T22 = adverso
    "queda_relevante_pen": -7.0,  # variação de penetração (pp do eleitorado) <= -7 pp = queda relevante (quartil pior dos redutos; Brasil = -4,7 pp)
    "abst_alta": 25.0,          # abstenção 1T26 >= 25% = alta
    "abst_cresc": 2.0,          # abstenção 1T26 - abstenção histórica >= +2 pp = crescente
    "disputa_aptos": 50_000,    # disputa exige eleitorado apto >= 50 mil
}


def norm(s):
    return re.sub(r"[^A-Z]", "", unicodedata.normalize("NFKD", str(s).upper()).encode("ascii", "ignore").decode())


# ---------------------------------------------------------------- de-para TSE x IBGE (oficial)
cm = json.loads((RAW / "tse_resultados" / "mun-cm.json").read_text())
depara = {m["cd"]: m["cdi"] for a in cm["abr"] for m in a["mu"] if m.get("cdi")}
nomes_tse = {m["cd"]: m["nm"] for a in cm["abr"] for m in a["mu"]}

# Área mínima comparável: Boa Esperança do Norte (MT) foi criada após 2022 a partir de Sorriso
# e Nova Ubiratã; os três viram uma unidade só nas comparações.
ibge_mun = json.loads((RAW / "ibge" / "municipios.json").read_text())
ibge_nome = {str(m["id"]): m["nome"] for m in ibge_mun}
by_name = {norm(m["nome"]): str(m["id"]) for m in ibge_mun if str(m["id"]).startswith("51")}
SORRISO, NOVA_UBIRATA, BOA_ESP = by_name["SORRISO"], by_name["NOVAUBIRATA"], by_name["BOAESPERANCADONORTE"]
AMC = {NOVA_UBIRATA: SORRISO, BOA_ESP: SORRISO}
AMC_NOME = {SORRISO: "Sorriso + Nova Ubiratã + Boa Esperança do Norte (AMC)"}


def amc(cd):
    return AMC.get(cd, cd)


# ---------------------------------------------------------------- TSE
def detalhe(ano):
    d = pd.read_csv(RAW / "tse" / f"detalhe_votacao_munzona_{ano}_BR.csv", sep=";", encoding="latin1",
                    dtype={"CD_MUNICIPIO": str})
    d = d.groupby(["NR_TURNO", "SG_UF", "CD_MUNICIPIO"])[
        ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS_BRANCOS", "QT_TOTAL_VOTOS_NULOS",
         "QT_VOTOS_NOMINAIS_VALIDOS"]].sum().reset_index()
    d.columns = ["turno", "uf", "tse", "aptos", "comp", "abst", "brancos", "nulos", "validos"]
    d["tse"] = d.tse.str.zfill(5)
    return d.groupby(["turno", "uf", "tse"]).sum().reset_index()


def candidatos(ano):
    d = pd.read_csv(RAW / "tse" / f"votacao_candidato_munzona_{ano}_BR.csv", sep=";", encoding="latin1",
                    dtype={"CD_MUNICIPIO": str},
                    usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_CANDIDATO", "NM_URNA_CANDIDATO",
                             "QT_VOTOS_NOMINAIS_VALIDOS"])
    d["CD_MUNICIPIO"] = d.CD_MUNICIPIO.str.zfill(5)  # alguns arquivos trazem o código sem zero à esquerda
    return d


det22, det26 = detalhe(2022), detalhe(2026)
cand22, cand26 = candidatos(2022), candidatos(2026)
GERACAO = {
    2022: pd.read_csv(RAW / "tse" / "detalhe_votacao_munzona_2022_BR.csv", sep=";", encoding="latin1", nrows=1)[["DT_GERACAO", "HH_GERACAO"]].iloc[0].tolist(),
    2026: pd.read_csv(RAW / "tse" / "detalhe_votacao_munzona_2026_BR.csv", sep=";", encoding="latin1", nrows=1)[["DT_GERACAO", "HH_GERACAO"]].iloc[0].tolist(),
}


def pleito(det, cand, turno):
    base = det[det.turno == turno].drop(columns="turno").set_index(["uf", "tse"])
    c = cand[cand.NR_TURNO == turno].copy()
    c["k"] = np.select([c.NR_CANDIDATO == LULA, c.NR_CANDIDATO == ADV], ["lula", "adv"], "outros")
    pv = c.pivot_table(index=["SG_UF", "CD_MUNICIPIO"], columns="k", values="QT_VOTOS_NOMINAIS_VALIDOS",
                       aggfunc="sum", fill_value=0)
    pv.index.names = ["uf", "tse"]
    base = base.join(pv, how="left").fillna(0)
    if "outros" not in base:
        base["outros"] = 0
    base["bn"] = base.brancos + base.nulos
    return base.reset_index()


t1_22 = pleito(det22, cand22, 1)
t2_22 = pleito(det22, cand22, 2)
t1_26 = pleito(det26, cand26, 1)

NOMES_CAND = {
    "lula": "Lula (PT)",
    "adv22": cand22[(cand22.NR_CANDIDATO == ADV)].NM_URNA_CANDIDATO.iloc[0].title() + " (PL)",
    "adv26": cand26[(cand26.NR_CANDIDATO == ADV)].NM_URNA_CANDIDATO.iloc[0].title() + " (PL)",
}
OUTROS26 = (cand26[~cand26.NR_CANDIDATO.isin([LULA, ADV])].groupby("NM_URNA_CANDIDATO").QT_VOTOS_NOMINAIS_VALIDOS.sum()
            .sort_values(ascending=False))

# ---------------------------------------------------------------- unidade: município IBGE (AMC)
F = ["aptos", "comp", "abst", "bn", "validos", "lula", "adv", "outros"]


def to_unit(df, suf):
    df = df.copy()
    df["ibge"] = np.where(df.uf == "ZZ", "ZZ" + df.tse, df.tse.map(depara))
    if df.ibge.isna().any():
        raise SystemExit(f"Sem de-para IBGE: {df[df.ibge.isna()][['uf', 'tse']].values.tolist()}")
    df["id"] = df.ibge.map(amc)
    g = df.groupby(["id", "uf"])[F].sum()
    g.columns = [f"{c}_{suf}" for c in F]
    return g


U = to_unit(t2_22, "22").join(to_unit(t1_26, "26"), how="outer").join(
    to_unit(t1_22, "1t22")[["aptos_1t22", "abst_1t22"]], how="outer").fillna(0).reset_index()
U["regiao"] = U.uf.map(REGIAO)
U["nome"] = U.id.map(lambda i: AMC_NOME.get(i, ibge_nome.get(i)))
ext = U.uf == "ZZ"
U.loc[ext, "nome"] = "Exterior"

# ---------------------------------------------------------------- socioeconômico (por id IBGE/AMC)
sid = RAW / "ibge" / "sidra"


def sidra(nome, var=None, **filtros):
    d = pd.read_csv(sid / f"{nome}.csv", dtype=str)
    if var:
        d = d[d.D2C == str(var)]
    for k, v in filtros.items():
        d = d[d[k].isin([str(x) for x in (v if isinstance(v, list) else [v])])]
    d["V"] = pd.to_numeric(d.V, errors="coerce")
    return d.groupby("D1C").V.sum()


soc = pd.DataFrame({
    "pop": sidra("pop_dens", 93),
    "area": sidra("pop_dens", 93) / sidra("pop_dens", 614),
    "domicilios": sidra("domicilios", 381),
    "urbana": sidra("urbana", 1000093),
    "negra": sidra("cor_raca", 1000093),
    "alfab": sidra("alfabetizacao", 2513),
    "superior": sidra("superior", 1002667),
    "renda_media": sidra("renda", 13431),
    "renda_mediana": sidra("renda", 13534),
    "evangelicos": sidra("religiao", 1000950, D4C=95277),
    "catolicos": sidra("religiao", 1000950, D4C=95263),
    "pib": sidra("pib", 37) * 1000,  # mil R$ -> R$
})
mds = pd.read_csv(RAW / "mds" / "bolsa_familia.csv", dtype={"codigo_ibge": str})
MDS_MES = str(mds.anomes_s.iloc[0])
cod6 = {k[:6]: k for k in ibge_nome}
mds["id"] = mds.codigo_ibge.map(cod6)
mds = mds.dropna(subset=["id"]).groupby("id")[["qtd_familias_beneficiarias_bolsa_familia_i",
                                                 "qtd_pessoas_beneficiarias_bolsa_familia_i"]].sum()
soc = soc.join(mds.rename(columns={"qtd_familias_beneficiarias_bolsa_familia_i": "pbf_fam",
                                   "qtd_pessoas_beneficiarias_bolsa_familia_i": "pbf_pes"}), how="outer")
soc.index.name = "ibge"
soc = soc.reset_index()
soc["id"] = soc.ibge.map(amc)
# média ponderada pela população dentro da AMC; somas para contagens
pct = ["urbana", "negra", "alfab", "superior", "renda_media", "renda_mediana", "evangelicos", "catolicos"]
for c in pct:
    soc[c + "_w"] = soc[c] * soc["pop"]
sg = soc.groupby("id").sum(numeric_only=True)
for c in pct:
    sg[c] = sg[c + "_w"] / sg["pop"]
sg = sg[["pop", "area", "domicilios", "pib", "pbf_fam", "pbf_pes"] + pct]
sg["densidade"] = sg["pop"] / sg["area"]
sg["pib_pc"] = sg.pib / sg["pop"]
sg["pbf_pop"] = 100 * sg.pbf_pes / sg["pop"]
sg["pbf_dom"] = 100 * sg.pbf_fam / sg.domicilios

perf = pd.read_csv(RAW / "tse" / "perfil_eleitorado_2026_mun.csv", dtype={"CD_MUNICIPIO": str})
perf["CD_MUNICIPIO"] = perf.CD_MUNICIPIO.str.zfill(5)
perf["id"] = perf.CD_MUNICIPIO.map(depara).map(amc)
perf = perf.groupby("id")[["QT_ELEITORES", "fem", "jov", "ido", "baixa", "sup"]].sum()
for c in ["fem", "jov", "ido", "baixa", "sup"]:
    sg["el_" + c] = 100 * perf[c] / perf.QT_ELEITORES

U = U.merge(sg.reset_index().rename(columns={"index": "id"}), on="id", how="left")


# ---------------------------------------------------------------- métricas
def metricas(d):
    """Calcula as métricas derivadas a partir das somas (vale p/ município, UF, região, Brasil)."""
    d = d.copy()
    for s in ("22", "26"):
        d[f"pv_l{s}"] = 100 * d[f"lula_{s}"] / d[f"validos_{s}"]
        d[f"pv_a{s}"] = 100 * d[f"adv_{s}"] / d[f"validos_{s}"]
        d[f"pen_l{s}"] = 100 * d[f"lula_{s}"] / d[f"aptos_{s}"]
        d[f"pen_a{s}"] = 100 * d[f"adv_{s}"] / d[f"aptos_{s}"]
        d[f"abs{s}"] = 100 * d[f"abst_{s}"] / d[f"aptos_{s}"]
        d[f"bnp{s}"] = 100 * d[f"bn_{s}"] / d[f"comp_{s}"]
        d[f"saldo{s}"] = d[f"lula_{s}"] - d[f"adv_{s}"]
        d[f"saldo_pp{s}"] = d[f"pv_l{s}"] - d[f"pv_a{s}"]
    d["pv_o26"] = 100 * d.outros_26 / d.validos_26
    d["d_lula"] = d.lula_26 - d.lula_22
    d["d_adv"] = d.adv_26 - d.adv_22
    d["d_pen_l"] = d.pen_l26 - d.pen_l22
    d["d_pen_a"] = d.pen_a26 - d.pen_a22
    d["d_pv_l"] = d.pv_l26 - d.pv_l22
    d["d_pv_a"] = d.pv_a26 - d.pv_a22
    d["d_saldo"] = d.saldo26 - d.saldo22
    d["d_saldo_pp"] = d.saldo_pp26 - d.saldo_pp22
    d["d_abs"] = d.abs26 - d.abs22
    d["d_aptos"] = d.aptos_26 - d.aptos_22
    d["d_aptos_pct"] = 100 * d.d_aptos / d.aptos_22
    d["abs_hist"] = 100 * (d.abst_1t22 + d.abst_22) / (d.aptos_1t22 + d.aptos_22)
    d["abs_exc_pp"] = d.abs26 - d.abs_hist
    d["abst_exc"] = (d.abs_exc_pp.clip(lower=0) / 100 * d.aptos_26)
    # Para onde foi o voto perdido (identidade contábil em frações do eleitorado apto, na escala de 2026):
    # perda_pen = Δabst + Δ(brancos+nulos) + terceiros + Δadversário (todos em pp do eleitorado)
    a26 = d.aptos_26
    d["perda_esc"] = -(d.d_pen_l) / 100 * a26  # votos de Lula perdidos, na escala do eleitorado 2026
    d["dest_abst"] = (d.abs26 - d.abs22) / 100 * a26
    d["dest_bn"] = (d.bn_26 / d.aptos_26 - d.bn_22 / d.aptos_22) * a26
    d["dest_terc"] = d.outros_26
    d["dest_adv"] = d.d_pen_a / 100 * a26
    # Estoque em disputa p/ 2T26
    d["estoque"] = d.outros_26 + d.bn_26 + d.abst_exc
    d["deficit"] = d.adv_26 - d.lula_26  # >0 = Lula atrás
    d["virada"] = np.select([d.deficit <= 0, d.estoque > d.deficit], ["frente", "possivel"], "dificil")
    d["sit_saldo"] = np.select(
        [(d.saldo22 > 0) & (d.saldo26 < 0), (d.saldo22 < 0) & (d.saldo26 > 0), d.d_saldo_pp < 0],
        ["virou_contra", "virou_favor", "encolheu"], "aumentou")
    d["potencial"] = (-d.d_pen_l).clip(lower=0) / 100 * a26 + d.abst_exc * d.pv_l22 / 100
    return d


U = metricas(U)


def segmento(d):
    reduto = d.pv_l22 >= P["reduto_pv"]
    return np.select(
        [reduto & (d.d_pen_l <= P["queda_relevante_pen"]),
         reduto & ((d.abs26 >= P["abst_alta"]) | (d.abs_exc_pp >= P["abst_cresc"])),
         (d.pv_l22 >= P["adverso_pv"]) & (d.pv_l22 < P["reduto_pv"]) & (d.aptos_26 >= P["disputa_aptos"]),
         reduto,
         d.pv_l22 < P["adverso_pv"]],
        ["reconquista", "mobilizacao", "disputa", "consolidado", "adverso"], "equilibrio")


U["seg"] = np.where(U.uf == "ZZ", "exterior", segmento(U))

# ---------------------------------------------------------------- agregados
SOMAS = ["aptos_22", "comp_22", "abst_22", "bn_22", "validos_22", "lula_22", "adv_22", "outros_22",
         "aptos_26", "comp_26", "abst_26", "bn_26", "validos_26", "lula_26", "adv_26", "outros_26",
         "aptos_1t22", "abst_1t22"]


def agrega(df, by):
    g = df.groupby(by)[SOMAS].sum().reset_index()
    g = metricas(g)
    # estoque/potencial agregados = soma dos municipais (o excesso de abstenção é local)
    s = df.groupby(by)[["abst_exc", "estoque", "potencial"]].sum().reset_index()
    g = g.drop(columns=["abst_exc", "estoque", "potencial"]).merge(s, on=by)
    g["virada"] = np.select([g.deficit <= 0, g.estoque > g.deficit], ["frente", "possivel"], "dificil")
    return g


mun = U[U.uf != "ZZ"]
UF = agrega(U, "uf")
UF["regiao"] = UF.uf.map(REGIAO)
REG = agrega(U, "regiao")
U["br"] = "Brasil"
BR = agrega(U, "br").iloc[0]
BR_MUN = agrega(mun.assign(br="Brasil"), "br").iloc[0]

# ---------------------------------------------------------------- perfil socioeconômico por segmento
IND = {
    "pv_l22": ("Lula % válidos 2T22", "%"),
    "renda_media": ("Renda domiciliar per capita média (R$)", "R$"),
    "renda_mediana": ("Renda domiciliar per capita mediana (R$)", "R$"),
    "pib_pc": ("PIB per capita 2022 (R$)", "R$"),
    "pbf_pop": ("Pessoas no Bolsa Família (% pop.)", "%"),
    "urbana": ("População urbana (%)", "%"),
    "negra": ("Preta + parda (%)", "%"),
    "alfab": ("Alfabetização 15+ (%)", "%"),
    "superior": ("Superior completo 18+ (%)", "%"),
    "evangelicos": ("Evangélicos 15+ (%)", "%"),
    "catolicos": ("Católicos 15+ (%)", "%"),
    "densidade": ("Densidade (hab/km²)", "hab/km²"),
    "el_jov": ("Eleitorado 16–24 anos (%)", "%"),
    "el_ido": ("Eleitorado 60+ (%)", "%"),
    "el_fem": ("Eleitorado feminino (%)", "%"),
    "el_baixa": ("Eleitorado até fund. incompleto (%)", "%"),
    "el_sup": ("Eleitorado com superior completo (%)", "%"),
}


def wmean(x, w):
    m = x.notna() & w.notna()
    return float(np.average(x[m], weights=w[m])) if m.any() else None


def wcorr(x, y, w):
    m = x.notna() & y.notna() & w.notna()
    x, y, w = x[m], y[m], w[m]
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return float(cov / math.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))


SEGS = ["reconquista", "mobilizacao", "disputa", "consolidado", "equilibrio", "adverso"]
perfil = []
for s in SEGS + ["todos"]:
    d = mun if s == "todos" else mun[mun.seg == s]
    row = {"seg": s, "n": int(len(d)), "aptos_26": int(d.aptos_26.sum()), "d_lula": int(d.d_lula.sum()),
           "potencial": int(d.potencial.sum()), "estoque": int(d.estoque.sum()),
           "d_pen_l": wmean(d.d_pen_l, d.aptos_26), "abs26": wmean(d.abs26, d.aptos_26),
           "d_abs": wmean(d.d_abs, d.aptos_26)}
    row.update({k: wmean(d[k], d.aptos_26) for k in IND})
    perfil.append(row)
correl = {k: {"d_pen_l": wcorr(mun[k], mun.d_pen_l, mun.aptos_26),
              "d_abs": wcorr(mun[k], mun.d_abs, mun.aptos_26),
              "pv_l26": wcorr(mun[k], mun.pv_l26, mun.aptos_26)} for k in IND if k != "pv_l22"}

# ---------------------------------------------------------------- validação contra o TSE
OFICIAL_2T22 = {"lula": 60_345_999, "adv": 58_206_354}  # resultado oficial TSE, 2º turno 2022
val = []
for uf in sorted(set(t1_26.uf)) + ["BR"]:
    js = json.loads((RAW / "tse_resultados" / f"{uf.lower()}-c0001-e006257-u.json").read_text())
    cands = {int(c["n"]): int(c["vap"]) for a in js["carg"][0]["agr"] for p in a["par"] for c in p["cand"]}
    sel = t1_26 if uf == "BR" else t1_26[t1_26.uf == uf]
    sel22 = t2_22 if uf == "BR" else t2_22[t2_22.uf == uf]
    val.append({
        "uf": uf,
        "lula_1t26": int(sel.lula.sum()), "lula_1t26_tse": cands.get(LULA),
        "adv_1t26": int(sel.adv.sum()), "adv_1t26_tse": cands.get(ADV),
        "validos_1t26": int(sel.validos.sum()), "validos_1t26_tse": int(js["v"]["vv"]),
        "lula_2t22": int(sel22.lula.sum()), "adv_2t22": int(sel22.adv.sum()),
        "validos_2t22": int(sel22.validos.sum()),
        "soma_cand_2t22_ok": bool(int(sel22.lula.sum() + sel22.adv.sum()) == int(sel22.validos.sum())),
    })
val = pd.DataFrame(val)
val["ok_1t26"] = (val.lula_1t26 == val.lula_1t26_tse) & (val.adv_1t26 == val.adv_1t26_tse) & (val.validos_1t26 == val.validos_1t26_tse)
br_ok = bool(val[val.uf == "BR"].lula_2t22.iloc[0] == OFICIAL_2T22["lula"] and val[val.uf == "BR"].adv_2t22.iloc[0] == OFICIAL_2T22["adv"])
val.to_csv(OUT / "validacao.csv", index=False)
print(val.to_string())
print("2T22 Brasil confere com resultado oficial:", br_ok)
assert val.ok_1t26.all() and val.soma_cand_2t22_ok.all() and br_ok, "VALIDAÇÃO FALHOU"


# ---------------------------------------------------------------- saída
def tabela(df, cols, dec):
    """JSON colunar compacto: {cols, rows}."""
    out = []
    for r in df[cols].itertuples(index=False):
        row = []
        for c, v in zip(cols, r):
            if isinstance(v, (float, np.floating)):
                v = None if not np.isfinite(v) else (round(float(v), dec.get(c, 2)) if dec.get(c, 2) else int(round(v)))
            elif isinstance(v, (np.integer,)):
                v = int(v)
            row.append(v)
        out.append(row)
    return {"cols": cols, "rows": out}


INT = ["aptos_22", "comp_22", "abst_22", "bn_22", "validos_22", "lula_22", "adv_22",
       "aptos_26", "comp_26", "abst_26", "bn_26", "validos_26", "lula_26", "adv_26", "outros_26",
       "saldo22", "saldo26", "d_saldo", "d_lula", "d_adv", "d_aptos", "abst_exc", "estoque", "deficit",
       "perda_esc", "dest_abst", "dest_bn", "dest_terc", "dest_adv", "potencial", "pop", "pbf_pes"]
PCT = ["pv_l22", "pv_l26", "pv_a22", "pv_a26", "pv_o26", "pen_l22", "pen_l26", "pen_a22", "pen_a26",
       "d_pen_l", "d_pen_a", "d_pv_l", "d_pv_a", "saldo_pp22", "saldo_pp26", "d_saldo_pp",
       "abs22", "abs26", "d_abs", "abs_hist", "abs_exc_pp", "bnp22", "bnp26", "d_aptos_pct"]
SOC = ["renda_media", "renda_mediana", "pib_pc", "pbf_pop", "urbana", "negra", "alfab", "superior",
       "evangelicos", "catolicos", "densidade", "el_jov", "el_ido", "el_fem", "el_baixa", "el_sup"]
dec = {**{c: 0 for c in INT}, **{c: 2 for c in PCT}, **{c: 1 for c in SOC}, "renda_media": 0,
       "renda_mediana": 0, "pib_pc": 0, "densidade": 1}
MCOLS = ["id", "nome", "uf", "regiao", "seg", "sit_saldo", "virada"] + INT + PCT + SOC
UCOLS = ["uf", "regiao", "virada", "sit_saldo"] + [c for c in INT + PCT if c not in ("pop", "pbf_pes")]
RCOLS = ["regiao", "virada", "sit_saldo"] + [c for c in INT + PCT if c not in ("pop", "pbf_pes")]

# compatibiliza tipos para saída
for c in INT:
    U[c] = U[c].astype(float)

(OUT / "municipios.json").write_text(json.dumps(tabela(mun, MCOLS, dec), ensure_ascii=False, separators=(",", ":")))
(OUT / "ufs.json").write_text(json.dumps(tabela(UF, UCOLS, dec), ensure_ascii=False, separators=(",", ":")))
(OUT / "regioes.json").write_text(json.dumps(tabela(REG, RCOLS, dec), ensure_ascii=False, separators=(",", ":")))


def rnd(v):
    if isinstance(v, (float, np.floating)):
        return round(float(v), 3)
    if isinstance(v, np.integer):
        return int(v)
    return v


extracao = json.loads((RAW / "extracao.json").read_text())["data_extracao"]
meta = {
    "titulo": "Cenário Presidencial 2026 — 2T22 → 1T26",
    "data_extracao": extracao,
    "candidatos": NOMES_CAND,
    "outros_1t26": {k.title(): int(v) for k, v in OUTROS26.items()},
    "brasil": {k: rnd(BR[k]) for k in UCOLS if k not in ("uf", "regiao")},
    "brasil_sem_exterior": {k: rnd(BR_MUN[k]) for k in ["estoque", "potencial", "abst_exc"]},
    "parametros": P,
    "amc": {SORRISO: AMC_NOME[SORRISO], "membros": [SORRISO, NOVA_UBIRATA, BOA_ESP]},
    "indicadores": {k: {"rotulo": v[0], "unid": v[1]} for k, v in IND.items()},
    "perfil_segmentos": [{k: rnd(v) for k, v in r.items()} for r in perfil],
    "correlacoes": correl,
    "fontes": [
        {"nome": "TSE — Detalhe da votação e votação por candidato por município/zona, 2022 (1º e 2º turno)",
         "url": "https://dadosabertos.tse.jus.br/", "ciclo": "2022", "status": "oficial",
         "gerado": " ".join(GERACAO[2022])},
        {"nome": "TSE — Detalhe da votação e votação por candidato por município/zona, 2026 (1º turno)",
         "url": "https://dadosabertos.tse.jus.br/", "ciclo": "2026", "status": "oficial — totalização TSE, sujeito a atualização",
         "gerado": " ".join(GERACAO[2026])},
        {"nome": "TSE — Divulgação de resultados 1T26 (conferência por UF) e de-para TSE×IBGE",
         "url": "https://resultados.tse.jus.br/", "ciclo": "2026", "status": "oficial"},
        {"nome": "TSE — Perfil do eleitorado 2026 (sexo, idade, escolaridade)",
         "url": "https://dadosabertos.tse.jus.br/dataset/eleitorado-2026", "ciclo": "07/2026", "status": "oficial"},
        {"nome": "IBGE — Censo Demográfico 2022 (SIDRA: 4714, 4712, 9923, 9605, 9543, 10061, 10295, 10198)",
         "url": "https://sidra.ibge.gov.br/", "ciclo": "2022", "status": "oficial (defasado: 2022)"},
        {"nome": "IBGE — PIB dos Municípios (SIDRA 5938), per capita com população do Censo 2022",
         "url": "https://sidra.ibge.gov.br/tabela/5938", "ciclo": "2022", "status": "oficial (defasado: 2022)"},
        {"nome": f"MDS — MI Social, Bolsa Família por município ({MDS_MES[4:]}/{MDS_MES[:4]})",
         "url": "https://aplicacoes.mds.gov.br/sagi/", "ciclo": MDS_MES, "status": "oficial"},
        {"nome": "IBGE — Malha municipal (API de malhas v3, qualidade mínima)",
         "url": "https://servicodados.ibge.gov.br/api/docs/malhas?versao=3", "ciclo": "2022", "status": "oficial"},
    ],
    "validacao": {"ok": bool(val.ok_1t26.all() and br_ok), "oficial_2t22": OFICIAL_2T22,
                  "tabela": val.to_dict(orient="records")},
}
(OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- malhas simplificadas
def simplifica(path, key, amc_map=None, nd=3):
    g = json.loads(path.read_text())

    def r(c):
        if isinstance(c[0], (int, float)):
            return [round(c[0], nd), round(c[1], nd)]
        out = [r(x) for x in c]
        if out and isinstance(out[0][0], (int, float)):  # anel: remove pontos repetidos
            ded = [out[0]] + [p for i, p in enumerate(out[1:], 1) if p != out[i - 1]]
            return ded if len(ded) >= 4 else out
        return out

    feats = []
    for f in g["features"]:
        cid = f["properties"]["codarea"]
        props = {"id": amc_map(cid) if amc_map else cid}
        feats.append({"type": "Feature", "properties": props,
                      "geometry": {"type": f["geometry"]["type"], "coordinates": r(f["geometry"]["coordinates"])}})
    return {"type": "FeatureCollection", "features": feats}


UFCOD = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
         "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
         "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
(OUT / "geo_municipios.json").write_text(json.dumps(simplifica(RAW / "ibge" / "malha_municipios.geojson", "codarea", amc, 3), separators=(",", ":")))
(OUT / "geo_ufs.json").write_text(json.dumps(simplifica(RAW / "ibge" / "malha_ufs.geojson", "codarea", lambda c: UFCOD[c], 3), separators=(",", ":")))

print("\nBrasil:", {k: rnd(BR[k]) for k in ["lula_22", "lula_26", "adv_22", "adv_26", "pen_l22", "pen_l26", "abs22", "abs26", "perda_esc", "dest_abst", "dest_bn", "dest_terc", "dest_adv"]})
print(U[U.uf != "ZZ"].seg.value_counts().to_string())
for f in sorted(OUT.iterdir()):
    print(f"{f.name}: {f.stat().st_size / 1e6:.2f} MB")
