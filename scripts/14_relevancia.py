"""Relatório do filtro de relevância dos cards: total antes e depois, distribuição por tipo e programa, cortes perto do
limite (para calibrar) e o carrossel final dos lugares de validação (mesma seleção da tela).
Saída: docs/cards_relevancia.md
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CD = ROOT / "painel_publico" / "cards"
BR = json.loads((CD / "BR.json").read_text())
FONTES, URLS, RG = BR["fontes"], BR["urls"], BR["regras"]
COR = pd.DataFrame(json.loads((ROOT / "data_publico" / "cards_cortados.json").read_text()))
TIPO = {1: "Está aqui", 2: "Origem (autoria)", 3: "Antes e depois", 4: "Três tempos"}
LUGARES = [("Várzea (Recife, PE)", "2611606", "VARZEA"), ("Bom Jardim (Fortaleza, CE)", "2304400", "BOMJARDIM"),
           ("Guamá (Belém, PA)", "1501402", "GUAMA"), ("Exu (PE)", "2605301", None), ("Canudos (BA)", "2906824", None),
           ("Porto Alegre (RS)", "4314902", None)]


def br(n):
    return f"{n:,}".replace(",", ".")


# cards que ficaram (locais) e que existem para estado/Brasil
fica = []
for f in CD.glob("*.json"):
    if f.name == "BR.json":
        continue
    for i, m in json.loads(f.read_text())["mun"].items():
        fica += [{**c, "chave": i} for c in m["c"]]
        fica += [{**c, "chave": f"{i}|{k}"} for k, b in m["b"].items() for c in b["cards"]]
F = pd.DataFrame(fica)
antes = pd.concat([F, COR], ignore_index=True)


def dist(d):
    return d.assign(tipo=d.tipo.map(TIPO)).groupby(["tipo", "prog"]).size()


t = pd.DataFrame({"antes": dist(antes), "depois": dist(F)}).fillna(0).astype(int).reset_index()
md = ["# Filtro de relevância dos cards", "",
      f"**Cards locais (bairro e cidade): {br(len(antes))} antes → {br(len(F))} depois do filtro.** "
      f"Estado e Brasil: {br(sum(len(v) for v in BR['uf'].values()) + len(BR['br']))} cards, que só entram quando o lugar tem menos de "
      f"{RG['amplos']} cards locais. Teto: {RG['max']} por lugar e {RG['prog']} por programa.", "",
      "## Distribuição por tipo e programa", "", "| Tipo | Programa | Antes | Depois |", "|---|---|---:|---:|"]
md += [f"| {r.tipo} | {r.prog} | {br(r.antes)} | {br(r.depois)} |" for r in t.itertuples()]
cid = F[~F.chave.str.contains("|", regex=False)].groupby("chave").size()
bai = F[F.chave.str.contains("|", regex=False)].chave.nunique()
md += ["", "## Cobertura", "",
       f"- Cidades com pelo menos 1 card local: {br(len(cid))} de 5.570; com menos de {RG['amplos']} (recebem estado/Brasil): "
       f"{br(int((cid < RG['amplos']).sum()) + 5570 - len(cid))}.",
       f"- Bairros com card próprio: {br(bai)}.", "",
       "## Motivo dos cortes", "", "| Motivo | Programa | Cards |", "|---|---|---:|"]
md += [f"| {m} | {p} | {br(n)} |" for (m, p), n in COR.groupby(["motivo", "prog"]).size().items()]
# perto do limite: os maiores "margem" abaixo de 1, espalhados por programa
perto = COR[(COR.motivo == "abaixo do limite de relevância") & (COR.margem < 1) & (COR.margem >= 0.75)].copy()
QUOTA = {"Bolsa Família": 2, "Mais Médicos": 2, "Cisternas": 1, "Pé-de-Meia": 1, "Infraestrutura (Censo)": 2,
         "Pobreza (Atlas)": 1, "Mortalidade infantil (Atlas)": 1}
ex = []
for prog, q in QUOTA.items():
    p = perto[(perto.prog == prog) & perto.modelo.isin(["BF-HOJE", "MM-HOJE", "CISTERNAS", "PDM-HOJE", "CENSO-BAIRRO", "POBREZA-MUN", "MORT-INF-MUN"])]
    p = p.sort_values("margem", ascending=False).drop_duplicates("lugar")
    # um no limite e, quando há cota 2, outro um pouco mais longe (margem ~0,85) para calibrar
    ex += p.head(1).to_dict("records") + (p.iloc[[(p.margem - 0.85).abs().argmin()]].to_dict("records") if q > 1 and len(p) > 1 else [])
md += ["", "## 10 cards cortados perto do limite", "",
       "Margem = quanto o melhor critério do card atinge do limite (1,00 = no limite).", "",
       "| Programa | Lugar | Card | Regra medida | Margem |", "|---|---|---|---|---:|"]
md += [f"| {e['prog']} | {e['lugar']} | {e['texto']} | {e['regra']} | {e['margem']:.2f} |" for e in ex]


def carrossel(i, b):
    a = BR["arq"].get(i)
    d = json.loads((CD / f"{a}.json").read_text())["mun"].get(i, {"c": [], "b": {}}) if a else {"c": [], "b": {}}
    loc, por = [], {}
    for c in sorted((d["b"].get(b, {}).get("cards", []) if b else []) + d["c"], key=lambda c: -c.get("s", 0)):
        if len(loc) >= RG["max"] or por.get(c["prog"], 0) >= RG["prog"]:
            continue
        por[c["prog"]] = por.get(c["prog"], 0) + 1
        loc.append(c)
    amp = []
    if len(loc) < RG["amplos"]:
        amp = sorted(BR["uf"].get(UF[i], []) + BR["br"], key=lambda c: -c.get("s", 0))[:RG["max"] - len(loc)]
    return loc, amp


UF = {r[0]: r[2] for r in json.loads((ROOT / "data" / "municipios.json").read_text())["rows"]}
md += ["", "## Carrossel final dos lugares de validação", ""]
for rot, i, b in LUGARES:
    loc, amp = carrossel(i, b)
    md += [f"**{rot}**", "", "| # | Nível | Card | Pontuação | Fonte |", "|---|---|---|---:|---|"]
    md += [f"| {k} | {c['nivel']} | {c['texto']} | {c.get('s', 0):.2f} | [{FONTES.get(str(c['fonte']), c['fonte'])}]({URLS.get(str(c['url']), c['url'])}){f" · [norma]({c['url2']})" if c.get('url2') else ''} |"
           for k, c in enumerate(loc + amp, 1)]
    md += [""]
(ROOT / "docs" / "cards_relevancia.md").write_text("\n".join(md) + "\n")
print("✓ docs/cards_relevancia.md")
