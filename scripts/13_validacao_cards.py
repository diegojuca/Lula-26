"""Relatório de validação dos cards (lugares definidos em LUGARES): cards gerados e bloqueados, com valor, janela,
fonte e link. Saída: docs/cards_validacao.md
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CD = ROOT / "painel_publico" / "cards"
BR = json.loads((CD / "BR.json").read_text())
BLOQ = json.loads((ROOT / "data_publico" / "cards_bloqueados.json").read_text())
FONTES, URLS = BR["fontes"], BR["urls"]

# (rótulo, código IBGE, chave do bairro ou None)
LUGARES = [
    ("Várzea (Recife, PE) — bairro", "2611606", "VARZEA"),
    ("Bom Jardim (Fortaleza, CE) — bairro", "2304400", "BOMJARDIM"),
    ("Guamá (Belém, PA) — bairro", "1501402", "GUAMA"),
    ("Exu (PE) — cidade pequena do semiárido", "2605301", None),
    ("Canudos (BA) — cidade pequena do semiárido", "2906824", None),
    ("Porto Alegre (RS) — capital do Sul", "4314902", None),
]
ESTADOS = ["PE", "SP"]


def linha(c):
    fonte = FONTES.get(str(c.get("fonte")), c.get("fonte"))
    url = URLS.get(str(c.get("url")), c.get("url"))
    valor = c.get("grande") or " · ".join(f"{a}: {b}" for a, b in c.get("tres", []))
    return f"| {c['modelo']} | {c['nivel']} | {valor} | {c['texto']} | {c.get('fecho', '')} | {c.get('periodo', '')} | [{fonte}]({url}) |"


def bloqueados(chaves):
    out = []
    for b in BLOQ:
        if b.get("chave") in chaves:
            v = b.get("valor")
            out.append(f"| {b['modelo']} | {b['nivel']} | {b['motivo']} | {json.dumps(v, ensure_ascii=False) if v is not None else ''} |")
    return out


md = ["# Validação dos cards (antes de publicar)", "",
      "Cada lugar lista os cards **gerados** (texto final, valor, fecho, período, fonte com link) e os **bloqueados** com o motivo.",
      "Os cards de estado e Brasil aparecem para todos os lugares e estão no fim.", ""]
for rot, i, b in LUGARES:
    a = BR["arq"].get(i)
    d = json.loads((CD / f"{a}.json").read_text())["mun"].get(i, {"c": [], "b": {}}) if a else {"c": [], "b": {}}
    md += [f"## {rot}", ""]
    if b:
        cb = d["b"].get(b, {}).get("cards", [])
        md += ["**Cards do bairro**", "", "| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |", "|---|---|---|---|---|---|---|"]
        md += [linha(c) for c in cb] or ["| — | | | nenhum card de bairro | | | |"]
        md += [""]
    md += ["**Cards da cidade**", "", "| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |", "|---|---|---|---|---|---|---|"]
    md += [linha(c) for c in d["c"]] or ["| — | | | nenhum | | | |"]
    chaves = {i} | ({f"{i}|{b}"} if b else set())
    bl = bloqueados(chaves)
    md += ["", "**Bloqueados**", "", "| Modelo | Nível | Motivo | Valores |", "|---|---|---|---|"] + (bl or ["| — | | nenhum | |"]) + [""]
for uf in ESTADOS:
    md += [f"## Estado: {uf}", "", "| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |", "|---|---|---|---|---|---|---|"]
    md += [linha(c) for c in BR["uf"].get(uf, [])]
    md += ["", "**Bloqueados**", "", "| Modelo | Nível | Motivo | Valores |", "|---|---|---|---|"] + (bloqueados({uf}) or ["| — | | nenhum | |"]) + [""]
md += ["## Brasil", "", "| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |", "|---|---|---|---|---|---|---|"]
md += [linha(c) for c in BR["br"]]
md += ["", "**Bloqueados**", "", "| Modelo | Nível | Motivo | Valores |", "|---|---|---|---|"] + bloqueados({"BR"}) + [""]
tot = {}
for b in BLOQ:
    tot[b["motivo"].split(":")[0]] = tot.get(b["motivo"].split(":")[0], 0) + 1
md += ["## Bloqueios no país inteiro, por motivo", "", "| Motivo | Quantidade |", "|---|---:|"] + [f"| {k} | {v:,} |".replace(",", ".") for k, v in sorted(tot.items(), key=lambda x: -x[1])]
(ROOT / "docs" / "cards_validacao.md").write_text("\n".join(md) + "\n")
print("✓ docs/cards_validacao.md")
