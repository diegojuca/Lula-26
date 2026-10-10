"""Gera painel/painel_standalone.html: um único arquivo com os dados embutidos.

O painel/index.html lê ../data/*.json via fetch (precisa de servidor). O standalone
abre direto no celular/navegador, sem servidor e sem internet (não usa CDN).
Uso: python scripts/03_standalone.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["meta", "municipios", "ufs", "regioes", "geo_municipios", "geo_ufs"]

html = (ROOT / "painel" / "index.html").read_text()
data = {f: json.loads((ROOT / "data" / f"{f}.json").read_text()) for f in FILES}
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
marker = '<script>\n"use strict";'
assert marker in html
html = html.replace(marker, "<script>window.__DATA__=" + payload + ";</script>\n" + marker, 1)
out = ROOT / "painel" / "painel_standalone.html"
out.write_text(html)
print(f"✓ {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")
