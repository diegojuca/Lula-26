"""Censo 2000 e 2010 por bairro (IBGE, agregados por setor): água, esgoto e lixo, com a mesma definição nos dois Censos.

  2000 (Domicilio_UF.XLS): V0003 domicílios particulares permanentes · V0018 água da rede geral ·
                           V0030 esgoto via rede geral ou pluvial · V0048 lixo coletado
  2010 (Domicilio01_UF.csv): V002 · V012 · V017 · V035 (mesmas definições)

Agrega setores por (município, bairro), só onde o setor tem bairro nos dois Censos. Um bairro só é comparável se o
nome (normalizado) existir em 2000 e em 2010 no mesmo município e o número de domicílios não mudar de forma
implausível (0,6x a 2,5x). Saída: raw/censo/bairros_2000_2010.csv. Os arquivos do IBGE são apagados após o uso.
Uso: python scripts/10_censo_bairros.py [UF ...]
"""
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "raw" / "censo"
TMP = D / "tmp"
FTP = "https://ftp.ibge.gov.br/Censos"
U2000 = FTP + "/Censo_Demografico_2000/Dados_do_Universo/Agregado_por_Setores_Censitarios/Agregado_de_setores_2000_{uf}.zip"
U2010 = FTP + "/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/{uf}_20260615.zip"
UFS = sys.argv[1:] or "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split()
ARQ2000 = {"SP": ["SP_RM", "SP_Exclusive_RM"]}
ARQ2010 = {"SP": ["SP_Capital", "SP_Exceto_Capital"]}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).upper()).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", s)


def baixa(url, dest):
    if dest.exists():
        return dest
    with requests.get(url, stream=True, timeout=900) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    return dest


def xls_csv(zf, padrao, pasta):
    """Extrai um .XLS do zip (2000) e converte para CSV com o LibreOffice."""
    nome = next(n for n in zf.namelist() if re.search(padrao, n, re.I))
    alvo = pasta / Path(nome).name
    alvo.write_bytes(zf.read(nome))
    subprocess.run(["soffice", "--headless", "--convert-to", 'csv:Text - txt - csv (StarCalc):59,34,76', "--outdir", str(pasta), str(alvo)],
                   check=True, capture_output=True, timeout=900)
    return pd.read_csv(alvo.with_suffix(".csv"), sep=";", dtype=str, encoding="utf-8", on_bad_lines="skip")


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def censo2000(uf):
    partes = []
    for arq in ARQ2000.get(uf, [uf]):
        z = baixa(U2000.format(uf=arq), TMP / f"c2000_{arq}.zip")
        pasta = TMP / f"x2000_{arq}"
        pasta.mkdir(exist_ok=True)
        with zipfile.ZipFile(z) as zf:
            b = xls_csv(zf, r"Basico_[^/]*\.xls$", pasta)
            d = xls_csv(zf, r"Domicilio_[^/]*\.xls$", pasta)
        b = b[["Cod_setor", "Cod_municipio", "Nome_do_bairro"]]
        d = d[["Cod_setor", "V0003", "V0018", "V0030", "V0048"]]
        x = b.merge(d, on="Cod_setor")
        x.columns = ["setor", "mun", "bairro", "dpp", "agua", "esgoto", "lixo"]
        partes.append(x)
        z.unlink()
    return pd.concat(partes)


def censo2010(uf):
    partes = []
    for arq in ARQ2010.get(uf, [uf]):
        z = baixa(U2010.format(uf=arq), TMP / f"c2010_{arq}.zip")
        with zipfile.ZipFile(z) as zf:
            def ler(p):
                nome = next(n for n in zf.namelist() if re.search(p, n, re.I))
                return pd.read_csv(zf.open(nome), sep=";", dtype=str, encoding="latin1", on_bad_lines="skip")
            b = ler(r"/CSV/Basico_[^/]*\.csv$")
            d = ler(r"/CSV/Domicilio01_[^/]*\.csv$")
        b = b[["Cod_setor", "Cod_municipio", "Nome_do_bairro"]]
        d = d[["Cod_setor", "V002", "V012", "V017", "V035"]]
        x = b.merge(d, on="Cod_setor")
        x.columns = ["setor", "mun", "bairro", "dpp", "agua", "esgoto", "lixo"]
        partes.append(x)
        z.unlink()
    return pd.concat(partes)


def agrega(x, ano):
    x = x.copy()
    for c in ["dpp", "agua", "esgoto", "lixo"]:
        x[c] = num(x[c])
    x = x[x.bairro.notna() & (x.bairro.str.strip() != "")]
    x["mun"] = x.mun.str[:7]
    x["chave"] = x.bairro.map(norm)
    # setor com variável suprimida pelo IBGE: sai do numerador e do denominador
    ok = x[["agua", "esgoto", "lixo"]].notna().all(axis=1)
    x["dpp_ok"] = x.dpp.where(ok, 0)
    for c in ["agua", "esgoto", "lixo"]:
        x[c] = x[c].where(ok, 0)
    x["falta"] = (~ok).astype(int)
    g = x.groupby(["mun", "chave"]).agg(nome=("bairro", "first"), setores=("setor", "size"),
                                        dpp=("dpp", "sum"), dpp_ok=("dpp_ok", "sum"), agua=("agua", "sum"), esgoto=("esgoto", "sum"),
                                        lixo=("lixo", "sum"), faltando=("falta", "sum"))
    g.columns = [f"{c}_{ano}" if c not in ("nome",) else f"nome_{ano}" for c in g.columns]
    return g


TMP.mkdir(parents=True, exist_ok=True)
saida = D / "bairros_2000_2010.csv"
ja = pd.read_csv(saida, dtype=str) if saida.exists() else pd.DataFrame()
res = [ja] if len(ja) else []
for uf in UFS:
    if len(ja) and (ja.uf == uf).any():
        print("=", uf)
        continue
    a = agrega(censo2000(uf), 2000)
    b = agrega(censo2010(uf), 2010)
    m = a.join(b, how="inner").reset_index()
    m["uf"] = uf
    r = m.dpp_2010 / m.dpp_2000
    ok_falta = (m.faltando_2000 <= 0.05 * m.setores_2000) & (m.faltando_2010 <= 0.05 * m.setores_2010)
    m["comparavel"] = (r > 0.6) & (r < 2.5) & ok_falta & (m.dpp_ok_2000 >= 200)
    res.append(m)
    pd.concat(res).to_csv(saida, index=False)
    print(uf, "bairros nos dois Censos:", len(m), "comparáveis:", int(m.comparavel.sum()), flush=True)
print("✓", saida)
