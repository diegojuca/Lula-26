"""Motor de cards compartilháveis (versão pública).

Gera, para cada lugar (bairro → cidade → estado → Brasil), os cards que passam nas regras de config/cards.json e
registra os bloqueados com o motivo. Regras gerais:
  - número abaixo do mínimo do modelo → bloqueia;
  - piora na janela, ou "três tempos" sem contraste verdadeiro → bloqueia (nunca troca janela nem métrica);
  - dado mais velho que o limite → bloqueia;
  - texto sempre no nível do dado (bairro só com dado de bairro);
  - autoria só com norma conferida em config/autoria.json.
Saídas: painel_publico/cards/<UF>.json, painel_publico/cards/BR.json, data_publico/cards_bloqueados.json
Uso: python scripts/11_cards.py
"""
import json
import math
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW, DATA, CFG = ROOT / "raw", ROOT / "data", ROOT / "config"
OUT = ROOT / "painel_publico" / "cards"
OUT.mkdir(parents=True, exist_ok=True)
J = json.loads((CFG / "janelas.json").read_text())
A = json.loads((CFG / "autoria.json").read_text())
C = json.loads((CFG / "cards.json").read_text())
LIM = C["limites"]
HOJE = pd.Timestamp("2026-10-10")
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
UFN = {"AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
       "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
       "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí", "PR": "Paraná",
       "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
       "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"}
URL = {
    "mds": "https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php",
    "cgu_pdm": "https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia",
    "saude": "https://apidadosabertos.saude.gov.br/v1/",
    "censo2000": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2000/Dados_do_Universo/Agregado_por_Setores_Censitarios/",
    "censo2010": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/",
    "atlas": "https://www.ipeadata.gov.br/",
    "sidra6665": "https://sidra.ibge.gov.br/tabela/6665", "sidra9552": "https://sidra.ibge.gov.br/tabela/9552",
    "ipea_sm": "https://www.ipeadata.gov.br/", "ipca": "https://sidra.ibge.gov.br/tabela/1737",
}


# ---------------------------------------------------------------- utilidades
def n0(v):
    return f"{int(math.floor(v)):,}".replace(",", ".")


def p1(v):
    return f"{v:.1f}".replace(".", ",")


def reais(v):  # sempre truncado
    if v >= 1e9:
        return f"R$ {math.floor(v / 1e8) / 10:.1f} bilhões".replace(".", ",")
    if v >= 1e6:
        return f"R$ {math.floor(v / 1e5) / 10:.1f} milhões".replace(".", ",")
    if v >= 1e3:
        return f"R$ {n0(v / 1e3)} mil"
    return f"R$ {n0(v)}"


def mes_txt(ym):
    ym = str(ym)
    return f"{MESES[int(ym[4:6]) - 1]}/{ym[:4]}"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).upper()).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s)


def fecho(modelo):
    ok = [f for f in C["fechos_por_modelo"].get(modelo, []) if C["fechos"][f]["tipo"] != "risco" or C["fechos_de_risco"]]
    return C["fechos"][ok[0]]["texto"] if ok else ""


CARDS, BLOQ = {}, []


def add(chave, card):
    card["fecho"] = fecho(card["modelo"])
    CARDS.setdefault(chave, []).append(card)


def bloq(modelo, nivel, lugar, motivo, valor=None, chave=None):
    BLOQ.append({"modelo": modelo, "nivel": nivel, "lugar": lugar, "motivo": motivo, "valor": valor, "chave": chave})


# ---------------------------------------------------------------- dados base
mun = pd.DataFrame(**{k: v for k, v in zip(["data", "columns"], [json.loads((DATA / "municipios.json").read_text())["rows"],
                                                                   json.loads((DATA / "municipios.json").read_text())["cols"]])})
meta = json.loads((DATA / "meta.json").read_text())
AMC = {m: meta["amc"]["membros"][0] for m in meta["amc"]["membros"][1:]}
ibge_nome = {str(m["id"]): m["nome"] for m in json.loads((RAW / "ibge" / "municipios.json").read_text())}
cod7 = {k[:6]: k for k in ibge_nome}
NOME = dict(zip(mun.id, mun.nome))
UFDE = dict(zip(mun.id, mun.uf))


def lugar_cid(i):
    return f"{NOME[i]} ({UFDE[i]})"


# IPCA (número-índice mensal)
ipca = requests.get("https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all", timeout=120).json()[1:]
IPCA = {r["D3C"]: float(r["V"]) for r in ipca if r["V"] not in ("...", "-")}
IPCA_ULT = max(IPCA)

# ---------------------------------------------------------------- Bolsa Família (2004 →), com Auxílio Brasil (regular + extraordinário)
bf = pd.read_csv(RAW / "series" / "mds_mensal.csv", dtype={"codigo_ibge": str, "anomes_s": str})
bf["id"] = bf.codigo_ibge.map(cod7).map(lambda i: AMC.get(i, i))
bf["fam"] = bf.qtd_familias_beneficiarias_bolsa_familia_i.fillna(0) + bf.pab_qtd_fam_benef_i.fillna(0)
bf["val"] = bf.valor_repassado_bolsa_familia_f.fillna(0) + bf.pab_valor_pago_d.fillna(0) + bf.pab_extraordinario_valor_pago_d.fillna(0)
bf = bf.groupby(["id", "anomes_s"])[["fam", "val", "qtd_cisternas_entregues_total_mds_i"]].sum().reset_index()
bf["defl"] = bf.anomes_s.map(lambda m: IPCA.get(IPCA_ULT) / IPCA[m] if m in IPCA else np.nan)
bf["val_real"] = bf.val * bf.defl
BF_ULT = bf.groupby("anomes_s").fam.sum().loc[lambda x: x > 0].index.max()  # último mês com dado na fonte


def janela(df, j, col="anomes_s"):
    ini = (J[j]["inicio"] or "1900-01").replace("-", "")
    fim = (J[j]["fim"] or "2100-12").replace("-", "")
    return df[(df[col] >= ini) & (df[col] <= fim)]


fed = pd.read_csv(RAW / "federal" / "federal_municipios.csv", dtype={"ibge": str})
fed["id"] = fed.ibge.map(lambda i: AMC.get(i, i))
fed = fed.groupby("id")[["pdm_parcelas", "pdm_valor", "mm_medicos"]].sum(min_count=1)
fmeta = json.loads((RAW / "federal" / "federal_meta.json").read_text())
PDM_MES, MM_REF = fmeta["pdm_mes"], fmeta["mm_referencia"]


def meses_desde(ym):
    ym = str(ym).replace("-", "")[:6]
    return (HOJE.year - int(ym[:4])) * 12 + HOJE.month - int(ym[4:6])


for i, g in bf.groupby("id"):
    if i not in NOME:
        continue
    L = lugar_cid(i)
    ult = g[g.anomes_s == BF_ULT]
    fam = float(ult.fam.sum()) if len(ult) else 0
    val = float(ult.val.sum()) if len(ult) else 0
    base = {"nivel": "cidade", "lugar": L, "fonte": "MDS, MI Social", "periodo": mes_txt(BF_ULT), "url": URL["mds"]}
    if meses_desde(BF_ULT) > LIM["BF-HOJE"]["dado_max_meses"]:
        bloq("BF-HOJE", "cidade", L, "dado velho", BF_ULT, i)
    elif fam >= LIM["BF-HOJE"]["min"]:
        add(i, {**base, "modelo": "BF-HOJE", "tipo": 1, "cat": "hoje", "grande": n0(fam), "rotulo": "famílias",
                "texto": f"{L}: {n0(fam)} famílias recebem o Bolsa Família."})
        a = A["bolsa_familia"]
        add(i, {**base, "modelo": "BF-ORIGEM", "tipo": 2, "cat": "historia", "grande": "2003", "rotulo": "criado em",
                "texto": f"O Bolsa Família, que hoje atende {n0(fam)} famílias em {NOME[i]}, foi criado em 2003, no governo Lula.",
                "fonte": f"Planalto ({a['norma']}); MDS", "periodo": f"2003; {mes_txt(BF_ULT)}", "url": a["url"]})
    else:
        bloq("BF-HOJE", "cidade", L, "número pequeno", fam, i)
    if val >= LIM["BF-VALOR"]["min"]:
        add(i, {**base, "modelo": "BF-VALOR", "tipo": 1, "cat": "hoje", "grande": reais(val), "rotulo": f"em {mes_txt(BF_ULT)}",
                "texto": f"{L}: o Bolsa Família pagou {reais(val)} às famílias daqui em {mes_txt(BF_ULT)}."})
    else:
        bloq("BF-VALOR", "cidade", L, "número pequeno", val, i)
    # três tempos: média mensal de famílias e valor real médio por família (R$ do último IPCA)
    t = {}
    for j in ("lula12", "temer_bolsonaro", "lula3"):
        w = janela(g, j)
        w = w[w.fam > 0]
        t[j] = (w.fam.mean(), (w.val_real.sum() / w.fam.sum()) if w.fam.sum() else np.nan)
    tb_f, tb_v = t["temer_bolsonaro"]
    motivos = []
    if any(pd.isna(x) for v in t.values() for x in v):
        motivos.append("série incompleta em alguma janela")
    elif tb_f > min(t["lula12"][0], t["lula3"][0]):
        motivos.append("famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula")
    if not motivos and tb_v > min(t["lula12"][1], t["lula3"][1]):
        motivos.append("valor médio real por família em Temer/Bolsonaro (inclui Auxílio Brasil) maior que numa janela Lula")
    if motivos:
        bloq("BF-3T", "cidade", L, "contraste não verdadeiro: " + "; ".join(motivos),
             {k: [None if pd.isna(v[0]) else round(v[0]), None if pd.isna(v[1]) else round(v[1], 2)] for k, v in t.items()}, i)
    else:
        add(i, {**base, "modelo": "BF-3T", "tipo": 4, "cat": "comparacao", "grande": "", "rotulo": "",
                "texto": f"{L}: famílias atendidas pelo Bolsa Família, média mensal por governo.",
                "tres": [["Lula 1 e 2", n0(t['lula12'][0])], ["Temer e Bolsonaro", n0(tb_f)], ["Lula 3", n0(t['lula3'][0])]],
                "periodo": f"jan/2004 a {mes_txt(BF_ULT)}"})
    # cisternas (acumulado até o último mês com dado)
    cz = g[g.qtd_cisternas_entregues_total_mds_i > 0]
    if len(cz):
        ym = cz.anomes_s.max()
        n = float(cz[cz.anomes_s == ym].qtd_cisternas_entregues_total_mds_i.sum())
        if n >= LIM["CISTERNAS"]["min"]:
            add(i, {**base, "modelo": "CISTERNAS", "tipo": 1, "cat": "hoje", "grande": n0(n), "rotulo": "cisternas",
                    "texto": f"{L}: {n0(n)} cisternas foram entregues pelo programa federal de cisternas até {mes_txt(ym)}.",
                    "periodo": f"até {mes_txt(ym)}"})
        else:
            bloq("CISTERNAS", "cidade", L, "número pequeno", n, i)

# Pé-de-Meia e Mais Médicos (hoje)
for i, r in fed.iterrows():
    if i not in NOME:
        continue
    L = lugar_cid(i)
    if pd.notna(r.pdm_parcelas):
        if meses_desde(PDM_MES) > LIM["PDM-HOJE"]["dado_max_meses"]:
            bloq("PDM-HOJE", "cidade", L, "dado velho", PDM_MES, i)
        elif r.pdm_parcelas >= LIM["PDM-HOJE"]["min"]:
            add(i, {"modelo": "PDM-HOJE", "tipo": 1, "cat": "hoje", "nivel": "cidade", "lugar": L, "grande": n0(r.pdm_parcelas),
                    "rotulo": "parcelas", "texto": f"{L}: estudantes daqui receberam {n0(r.pdm_parcelas)} parcelas do Pé-de-Meia em {mes_txt(PDM_MES)}.",
                    "fonte": "CGU, Portal da Transparência", "periodo": mes_txt(PDM_MES), "url": URL["cgu_pdm"]})
        else:
            bloq("PDM-HOJE", "cidade", L, "número pequeno", r.pdm_parcelas, i)
    mm = r.mm_medicos
    if pd.notna(mm):
        ref = MM_REF.split("-")
        per = f"{ref[2]}/{ref[1]}/{ref[0]}"
        if mm >= LIM["MM-HOJE"]["min"]:
            add(i, {"modelo": "MM-HOJE", "tipo": 1, "cat": "hoje", "nivel": "cidade", "lugar": L, "grande": n0(mm), "rotulo": "médicos",
                    "texto": f"{L}: {n0(mm)} médicos do Mais Médicos atendem hoje.", "fonte": "Ministério da Saúde", "periodo": per, "url": URL["saude"]})
            a = A["mais_medicos"]
            add(i, {"modelo": "MM-RETOMADA", "tipo": 2, "cat": "historia", "nivel": "cidade", "lugar": L, "grande": "2023", "rotulo": "retomado em",
                    "texto": f"O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são {n0(mm)} médicos do programa em {NOME[i]}.",
                    "fonte": f"Planalto ({a['norma_retomada']}); Ministério da Saúde, {per}", "periodo": per, "url": a["url_retomada"]})
        else:
            bloq("MM-HOJE", "cidade", L, "número pequeno", mm, i)

# Mais Médicos, três tempos (Dilma × Temer/Bolsonaro × Lula 3), dezembro de cada ano
mmf = RAW / "series" / "mm_serie.csv"
MM_SERIE = set()
if mmf.exists():
    ms = pd.read_csv(mmf)
    ms["id"] = ms.ibge6.astype("Int64").astype(str).map(cod7).map(lambda i: AMC.get(i, i) if isinstance(i, str) else i)
    ms = ms.dropna(subset=["id"]).groupby(["id", "ano"]).ativos.sum().reset_index()
    for i, g in ms.groupby("id"):
        if i not in NOME:
            continue
        MM_SERIE.add(i)
        L = lugar_cid(i)
        dv = g[g.ano.between(2013, 2015)].ativos.mean()
        tb = g[g.ano.between(2016, 2022)].ativos.mean()
        l3 = g[g.ano >= 2023].ativos.mean()
        if not (l3 > tb) or l3 < LIM["MM-3T"]["min"]:
            bloq("MM-3T", "cidade", L, "contraste não verdadeiro ou número pequeno",
                 {"dilma": round(dv, 1), "temer_bolsonaro": round(tb, 1), "lula3": round(l3, 1)}, i)
        else:
            add(i, {"modelo": "MM-3T", "tipo": 4, "cat": "comparacao", "nivel": "cidade", "lugar": L, "grande": "", "rotulo": "",
                    "texto": f"{L}: médicos do Mais Médicos em dezembro, média por governo.",
                    "tres": [["Dilma", n0(dv)], ["Temer e Bolsonaro", n0(tb)], ["Lula 3", n0(l3)]],
                    "fonte": "Ministério da Saúde, série histórica do programa", "periodo": "dez/2013 a " + MM_REF[:4], "url": URL["saude"]})

# ---------------------------------------------------------------- Atlas Brasil (Censo 2000 × 2010), nível cidade
def ipea(serie):
    f = RAW / "series" / f"{serie}.json"
    if not f.exists():
        f.write_text(requests.get(f"https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{serie}')", timeout=300).text)
    v = json.loads(f.read_text())["value"]
    d = pd.DataFrame([(x["TERCODIGO"], x["VALDATA"][:4], x["VALVALOR"], x["NIVNOME"]) for x in v], columns=["ter", "ano", "v", "niv"])
    return d[d.niv == "Municípios"].pivot_table(index="ter", columns="ano", values="v")


DEC = "Entre 2000 e 2010, década em que Lula governou de 2003 a 2010,"
for serie, modelo, frase, lim in [("ADH_PMPOB", "POBREZA-MUN", "a parcela de pessoas pobres", LIM["POBREZA-MUN"]["min_pp"]),
                                  ("ADH_MORT1", "MORT-INF-MUN", "a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa)", LIM["MORT-INF-MUN"]["min_queda"])]:
    d = ipea(serie)
    for ter, r in d.iterrows():
        i = AMC.get(ter, ter)
        if i not in NOME or ter in AMC:
            continue
        a, b = r.get("2000"), r.get("2010")
        L = lugar_cid(i)
        if pd.isna(a) or pd.isna(b):
            bloq(modelo, "cidade", L, "sem dado", None, i)
            continue
        if a - b < lim:
            bloq(modelo, "cidade", L, "piora ou queda pequena", [a, b], i)
            continue
        un = "%" if modelo == "POBREZA-MUN" else ""
        add(i, {"modelo": modelo, "tipo": 3, "cat": "historia", "nivel": "cidade", "lugar": L,
                "grande": f"{p1(a)}{un} → {p1(b)}{un}", "rotulo": "2000 → 2010",
                "texto": f"{DEC} {frase} em {NOME[i]} caiu de {p1(a)}{un} para {p1(b)}{un}.",
                "fonte": "Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010", "periodo": "2000 e 2010", "url": URL["atlas"]})

# ---------------------------------------------------------------- Censo por bairro (2000 × 2010): água, esgoto, lixo
CB = {}
cb = pd.read_csv(RAW / "censo" / "bairros_2000_2010.csv", dtype={"mun": str})
IND = {"agua": "os domicílios com água da rede geral", "esgoto": "os domicílios com esgoto por rede geral",
       "lixo": "os domicílios com lixo coletado"}
for r in cb.itertuples():
    i = AMC.get(r.mun, r.mun)
    if i not in NOME:
        continue
    nomeb = str(r.nome_2010).strip().title() if str(r.nome_2010).isupper() else str(r.nome_2010).strip()
    chave = f"{i}|{r.chave}"
    CB[chave] = nomeb
    L = f"{nomeb}, {NOME[i]} ({UFDE[i]})"
    if not bool(r.comparavel):
        bloq("CENSO-BAIRRO", "bairro", L, "bairro sem correspondência segura entre 2000 e 2010", None, chave)
        continue
    for k, frase in IND.items():
        a = 100 * getattr(r, f"{k}_2000") / r.dpp_ok_2000
        b = 100 * getattr(r, f"{k}_2010") / r.dpp_ok_2010
        if b - a < LIM["CENSO-BAIRRO"]["min_pp"]:
            bloq(f"CENSO-BAIRRO-{k.upper()}", "bairro", L, "piora ou avanço pequeno", [round(a, 1), round(b, 1)], chave)
            continue
        add(chave, {"modelo": "CENSO-BAIRRO", "sub": k, "tipo": 3, "cat": "historia", "nivel": "bairro", "lugar": L,
                    "grande": f"{a:.0f}% → {b:.0f}%", "rotulo": "2000 → 2010",
                    "texto": f"{DEC} {frase} em {nomeb} ({NOME[i]}) passaram de {a:.0f}% para {b:.0f}%.",
                    "fonte": "IBGE, Censos 2000 e 2010 (agregados por setor)", "periodo": "2000 e 2010", "url": URL["censo2010"]})

# ---------------------------------------------------------------- UBS por bairro (hoje)
ubsf = RAW / "series" / "ubs.csv"
if ubsf.exists():
    u = pd.read_csv(ubsf, dtype=str)
    u["id"] = u.ibge.str[:6].map(cod7).map(lambda i: AMC.get(i, i) if isinstance(i, str) else i)
    u = u.dropna(subset=["id", "bairro"])
    u["chave"] = u.bairro.map(norm)
    for (i, ch), g in u.groupby(["id", "chave"]):
        if i not in NOME or not ch:
            continue
        chave = f"{i}|{ch}"
        nomeb = CB.get(chave) or g.bairro.iloc[0].title()
        L = f"{nomeb}, {NOME[i]} ({UFDE[i]})"
        n = len(g)
        if n < LIM["UBS-BAIRRO"]["min"]:
            bloq("UBS-BAIRRO", "bairro", L, "número pequeno", n, chave)
            continue
        add(chave, {"modelo": "UBS-BAIRRO", "tipo": 1, "cat": "hoje", "nivel": "bairro", "lugar": L, "grande": n0(n),
                    "rotulo": "unidades de saúde", "texto": f"{nomeb} ({NOME[i]}): {n} unidades básicas de saúde do SUS atendem o bairro.",
                    "fonte": "Ministério da Saúde, cadastro de UBS", "periodo": "out/2026", "url": URL["saude"]})

# ---------------------------------------------------------------- UF e Brasil
UFC = {}
fome_uf = requests.get("https://apisidra.ibge.gov.br/values/t/9552/n3/all/v/all/p/2023,2024/c1/6795/c12404/109102", timeout=120).json()[1:]
fu = {}
for r in fome_uf:
    if "percentual" in r["D2N"].lower() and "domic" in r["D2N"].lower():
        fu.setdefault(r["D1N"], {})[r["D3C"]] = float(r["V"])
SIGLA = {v: k for k, v in UFN.items()}
for nome_uf, v in fu.items():
    uf = SIGLA.get(nome_uf)
    if not uf or "2023" not in v or "2024" not in v:
        continue
    a, b = v["2023"], v["2024"]
    L = UFN[uf]
    if a - b < LIM["FOME-UF-L3"]["min_pp"]:
        bloq("FOME-UF-L3", "uf", L, "piora ou queda pequena", [a, b], uf)
        continue
    UFC.setdefault(uf, []).append({"modelo": "FOME-UF-L3", "tipo": 3, "cat": "historia", "nivel": "uf", "lugar": L,
                                   "grande": f"{p1(a)}% → {p1(b)}%", "rotulo": "2023 → 2024", "fecho": fecho("FOME-UF-L3"),
                                   "texto": f"Em {L}, os domicílios em insegurança alimentar grave (fome) caíram de {p1(a)}% em 2023 para {p1(b)}% em 2024, no governo Lula.",
                                   "fonte": "IBGE, PNAD Contínua, escala EBIA", "periodo": "2023 e 2024", "url": URL["sidra9552"]})
# somatórios por UF (Bolsa Família, Pé-de-Meia, Mais Médicos)
bu = bf[bf.anomes_s == BF_ULT].assign(uf=lambda d: d.id.map(UFDE)).groupby("uf")[["fam", "val"]].sum()
fu2 = fed.assign(uf=lambda d: d.index.map(UFDE)).groupby("uf")[["pdm_parcelas", "mm_medicos"]].sum()
for uf in UFN:
    L = UFN[uf]
    if uf in bu.index:
        UFC.setdefault(uf, []).append({"modelo": "BF-HOJE", "tipo": 1, "cat": "hoje", "nivel": "uf", "lugar": L, "grande": n0(bu.loc[uf, "fam"]),
                                       "rotulo": "famílias", "fecho": fecho("BF-HOJE"), "texto": f"Em {L}, {n0(bu.loc[uf, 'fam'])} famílias recebem o Bolsa Família.",
                                       "fonte": "MDS, MI Social", "periodo": mes_txt(BF_ULT), "url": URL["mds"]})
    if uf in fu2.index and fu2.loc[uf, "mm_medicos"] >= 3:
        UFC.setdefault(uf, []).append({"modelo": "MM-HOJE", "tipo": 1, "cat": "hoje", "nivel": "uf", "lugar": L, "grande": n0(fu2.loc[uf, "mm_medicos"]),
                                       "rotulo": "médicos", "fecho": fecho("MM-HOJE"), "texto": f"Em {L}, {n0(fu2.loc[uf, 'mm_medicos'])} médicos do Mais Médicos atendem hoje.",
                                       "fonte": "Ministério da Saúde", "periodo": MM_REF, "url": URL["saude"]})

BR = []
# Fome no Brasil (escala EBIA do IBGE, sem misturar com VIGISAN/PENSSAN)
fb = {r["D3C"]: float(r["V"]) for r in requests.get(
    "https://apisidra.ibge.gov.br/values/t/6665/n1/all/v/800/p/all/c12404/109102", timeout=120).json()[1:]}
if fb["2004"] - fb["2009"] >= LIM["FOME-BR"]["min_pp"]:
    BR.append({"modelo": "FOME-BR", "tipo": 3, "cat": "historia", "nivel": "brasil", "lugar": "Brasil", "grande": f"{p1(fb['2004'])}% → {p1(fb['2009'])}%",
               "rotulo": "2004 → 2009", "fecho": fecho("FOME-BR"),
               "texto": f"No Brasil, os domicílios em insegurança alimentar grave (fome) caíram de {p1(fb['2004'])}% em 2004 para {p1(fb['2009'])}% em 2009, no governo Lula.",
               "fonte": "IBGE, PNAD 2004 e 2009, escala EBIA", "periodo": "2004 e 2009", "url": URL["sidra6665"]})
if fb["2023"] - fb["2024"] >= LIM["FOME-BR"]["min_pp"]:
    BR.append({"modelo": "FOME-BR", "tipo": 3, "cat": "historia", "nivel": "brasil", "lugar": "Brasil", "grande": f"{p1(fb['2023'])}% → {p1(fb['2024'])}%",
               "rotulo": "2023 → 2024", "fecho": fecho("FOME-BR"),
               "texto": f"No Brasil, os domicílios em insegurança alimentar grave (fome) caíram de {p1(fb['2023'])}% em 2023 para {p1(fb['2024'])}% em 2024, no governo Lula.",
               "fonte": "IBGE, PNAD Contínua 2023 e 2024, escala EBIA", "periodo": "2023 e 2024", "url": URL["sidra6665"]})
# três tempos da fome: última medição de cada janela (Lula 1–2: 2009; Temer/Bolsonaro: 2018; Lula 3: 2024)
l12, tb, l3 = fb["2009"], fb["2018"], fb["2024"]
if not (l12 < tb and l3 < tb):
    bloq("FOME-3T", "brasil", "Brasil", f"contraste não verdadeiro: Lula 1–2 (2009) {p1(l12)}% não é menor que Temer/Bolsonaro (2018) {p1(tb)}%",
         {"2009": l12, "2018": tb, "2024": l3}, "BR")
# salário mínimo real (valor legal corrigido pelo IPCA)
smf = RAW / "series" / "MTE12_SALMIN12.json"
if not smf.exists():
    smf.write_text(requests.get("https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='MTE12_SALMIN12')", timeout=300).text)
SM = {x["VALDATA"][:7].replace("-", ""): x["VALVALOR"] for x in json.loads(smf.read_text())["value"]}
fimL3 = IPCA_ULT


def ganho(a, b):
    return 100 * ((SM[b] / SM[a]) / (IPCA[b] / IPCA[a]) - 1)


g12, gd, gtb, gl3 = ganho("200212", "201012"), ganho("201012", "201608"), ganho("201608", "202212"), ganho("202212", fimL3)
if g12 > gtb and gl3 > gtb:
    BR.append({"modelo": "SM-3T", "tipo": 4, "cat": "comparacao", "nivel": "brasil", "lugar": "Brasil", "grande": "", "rotulo": "",
               "fecho": fecho("SM-3T"), "texto": "Ganho real do salário mínimo (acima da inflação, IPCA) em cada governo.",
               "tres": [["Lula 1 e 2", f"+{p1(g12)}%"], ["Temer e Bolsonaro", f"+{p1(gtb)}%" if gtb >= 0 else f"{p1(gtb)}%"], ["Lula 3", f"+{p1(gl3)}%"]],
               "nota": f"Dilma: +{p1(gd)}%. Períodos: dez/2002–dez/2010; ago/2016–dez/2022; dez/2022–{mes_txt(fimL3)}.",
               "fonte": "Salário mínimo legal (Ipeadata) corrigido pelo IPCA (IBGE)", "periodo": f"dez/2002 a {mes_txt(fimL3)}", "url": URL["ipca"]})
else:
    bloq("SM-3T", "brasil", "Brasil", "contraste não verdadeiro", [g12, gtb, gl3], "BR")
a = A["minha_casa_minha_vida"]
BR.append({"modelo": "MCMV-ORIGEM", "tipo": 2, "cat": "historia", "nivel": "brasil", "lugar": "Brasil", "grande": "2009", "rotulo": "criado em",
           "fecho": fecho("MCMV-ORIGEM"), "texto": "O Minha Casa Minha Vida foi criado em 2009 e retomado em 2023, nos governos Lula.",
           "fonte": f"Planalto ({a['norma']}; {a['norma_retomada']})", "periodo": "2009 e 2023", "url": a["url"]})
nb = bf[bf.anomes_s == BF_ULT].fam.sum()
BR.append({"modelo": "BF-HOJE", "tipo": 1, "cat": "hoje", "nivel": "brasil", "lugar": "Brasil", "grande": n0(nb), "rotulo": "famílias",
           "fecho": fecho("BF-HOJE"), "texto": f"No Brasil, {n0(nb)} famílias recebem o Bolsa Família.", "fonte": "MDS, MI Social",
           "periodo": mes_txt(BF_ULT), "url": URL["mds"]})
for m, motivo in [("FMI", "fonte oficial não conferida neste ambiente (BCB/Fazenda)"), ("MAPA-FOME", "relatório SOFI/FAO não conferido neste ambiente"),
                  ("CAMPUS", "data oficial dos campi (MEC/Plataforma Nilo Peçanha) não disponível"),
                  ("EMPREGO-3T", "RAIS/CAGED (MTE) não responde a este ambiente")]:
    bloq(m, "brasil", "Brasil", motivo, None, "BR")

# ---------------------------------------------------------------- saída por UF (cidade + bairros) e Brasil
ORDEM = {"bairro": 0, "cidade": 1, "uf": 2, "brasil": 3}
porUF = {}
for chave, cs in CARDS.items():
    i, _, b = chave.partition("|")
    uf = UFDE.get(i)
    if not uf:
        continue
    d = porUF.setdefault(uf, {}).setdefault(i, {"c": [], "b": {}})
    if b:
        d["b"].setdefault(b, {"nome": CB.get(chave) or cs[0]["lugar"].split(",")[0], "cards": []})["cards"] += cs
    else:
        d["c"] += cs
# URLs e fontes viram códigos curtos (o dicionário vai no BR.json)
URLS, FONTES = {}, {}


def compacta(c):
    c = dict(c)
    for campo, tab in (("url", URLS), ("fonte", FONTES)):
        if c.get(campo):
            c[campo] = tab.setdefault(c[campo], len(tab))
    return c


for f in OUT.glob("*.json"):
    f.unlink()
# mesmo particionamento dos dados do lugar: arquivos de até ~MAX bytes, agrupando cidades em ordem de código
MAX = 400_000
arq_cards = {}
for uf, d in porUF.items():
    blocos, atual, tam = [], {}, 0
    for i in sorted(d):
        item = {"c": [compacta(c) for c in d[i]["c"]],
                "b": {k: {"nome": v["nome"], "cards": [compacta(c) for c in v["cards"]]} for k, v in d[i]["b"].items()}}
        n = len(json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode())
        if atual and tam + n > MAX:
            blocos.append(atual)
            atual, tam = {}, 0
        atual[i] = item
        tam += n
    blocos.append(atual)
    for k, bl in enumerate(blocos, 1):
        nome = uf if len(blocos) == 1 else f"{uf}-{k}"
        for i in bl:
            arq_cards[i] = nome
        (OUT / f"{nome}.json").write_text(json.dumps({"mun": bl}, ensure_ascii=False, separators=(",", ":")))
(OUT / "BR.json").write_text(json.dumps({"br": [compacta(c) for c in BR], "uf": {k: [compacta(c) for c in v] for k, v in UFC.items()},
                                         "urls": {v: k for k, v in URLS.items()}, "fontes": {v: k for k, v in FONTES.items()},
                                         "arq": arq_cards}, ensure_ascii=False, separators=(",", ":")))
(ROOT / "data_publico" / "cards_bloqueados.json").write_text(json.dumps(BLOQ, ensure_ascii=False, default=float))
tot = sum(len(v) for v in CARDS.values()) + sum(len(v) for v in UFC.values()) + len(BR)
print(f"cards gerados: {tot} | bloqueados: {len(BLOQ)} | séries do Mais Médicos carregadas: {len(MM_SERIE)}")
print(pd.Series([b["motivo"].split(":")[0] for b in BLOQ]).value_counts().to_string())
tam = {f.name: f.stat().st_size for f in OUT.glob("*.json")}
print("maior arquivo de cards:", max(tam, key=tam.get), round(max(tam.values()) / 1e3), "KB; total", round(sum(tam.values()) / 1e6, 1), "MB")
