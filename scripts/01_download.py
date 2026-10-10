"""Baixa as fontes públicas brutas para raw/ (não versionado).

Reexecutável: pula arquivos já baixados (use --force para rebaixar).

Fontes:
  TSE dados abertos (cdn.tse.jus.br)
    - votacao_candidato_munzona 2022 e 2026  -> só o CSV de Presidente (*_BR.csv)
    - detalhe_votacao_munzona   2022 e 2026  -> só o CSV de Presidente (*_BR.csv)
    - perfil_eleitorado 2026                 -> agregado por município (sexo, idade, escolaridade)
  TSE divulgação de resultados (resultados.tse.jus.br)
    - config de municípios (de-para TSE x IBGE oficial) e totais por UF do 1T26 (conferência)
  IBGE
    - malhas (servicodados v3), localidades, SIDRA (Censo 2022, PIB municipal)
  MDS
    - MI Social (Bolsa Família por município, mês mais recente)

Uso: python scripts/01_download.py [--force] [--skip-perfil]
"""
import io
import json
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
FORCE = "--force" in sys.argv
SKIP_PERFIL = "--skip-perfil" in sys.argv

TSE_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
TSE_RES = "https://resultados.tse.jus.br/oficial"
ELEICAO_2026_T1 = "6257"  # Eleição Ordinária Federal 2026, 1º turno (código da divulgação)
SIDRA = "https://apisidra.ibge.gov.br/values"
MDS = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB",
       "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
UF_COD = {"RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17, "MA": 21, "PI": 22,
          "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27, "SE": 28, "BA": 29, "MG": 31, "ES": 32,
          "RJ": 33, "SP": 35, "PR": 41, "SC": 42, "RS": 43, "MS": 50, "MT": 51, "GO": 52, "DF": 53}

S = requests.Session()


def get(url, **kw):
    for i in range(5):
        try:
            r = S.get(url, timeout=kw.pop("timeout", 300), **kw)
            r.raise_for_status()
            return r
        except Exception as e:  # rede instável: tenta de novo
            if i == 4:
                raise
            print(f"  retry {i + 1} {url[:90]}: {e}")
            time.sleep(2 ** (i + 1))


def download(url, dest: Path):
    if dest.exists() and not FORCE:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"↓ {url}")
    with S.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    return dest


def tse_zip_member(dataset, ano, member_suffix, dest: Path):
    """Baixa o zip do TSE, extrai só o membro desejado e apaga o zip."""
    if dest.exists() and not FORCE:
        print(f"= {dest.name}")
        return
    z = download(f"{TSE_CDN}/{dataset}/{dataset}_{ano}.zip", RAW / "tse" / f"{dataset}_{ano}.zip")
    with zipfile.ZipFile(z) as zf:
        name = next(n for n in zf.namelist() if n.endswith(member_suffix))
        dest.write_bytes(zf.read(name))
    z.unlink()
    print(f"✓ {dest.name}")


def perfil_eleitorado(ano=2026):
    dest = RAW / "tse" / f"perfil_eleitorado_{ano}_mun.csv"
    if dest.exists() and not FORCE:
        print(f"= {dest.name}")
        return
    z = download(f"{TSE_CDN}/perfil_eleitorado/perfil_eleitorado_{ano}.zip",
                 RAW / "tse" / f"perfil_eleitorado_{ano}.zip")
    cols = ["SG_UF", "CD_MUNICIPIO", "DS_GENERO", "CD_FAIXA_ETARIA", "CD_GRAU_ESCOLARIDADE", "QT_ELEITORES"]
    parts = []
    with zipfile.ZipFile(z) as zf:
        for uf in UFS:
            name = f"perfil_eleitorado_{ano}_{uf}.csv"
            with zf.open(name) as fh:
                for ch in pd.read_csv(fh, sep=";", encoding="latin1", usecols=cols,
                                      dtype={"CD_MUNICIPIO": str}, chunksize=2_000_000):
                    ch["fem"] = (ch.DS_GENERO == "FEMININO") * ch.QT_ELEITORES
                    # CD_FAIXA_ETARIA: AAXX (ex. 1600 = 16 anos, 2024 = 20 a 24, 6064 = 60 a 64)
                    idade_ini = ch.CD_FAIXA_ETARIA // 100
                    ch["jov"] = ((idade_ini >= 16) & (idade_ini <= 24)) * ch.QT_ELEITORES
                    ch["ido"] = (idade_ini >= 60) * ch.QT_ELEITORES
                    # CD_GRAU_ESCOLARIDADE: 1 analfabeto, 2 lê e escreve, 3 fund. incompleto, 8 superior completo
                    ch["baixa"] = ch.CD_GRAU_ESCOLARIDADE.isin([1, 2, 3]) * ch.QT_ELEITORES
                    ch["sup"] = (ch.CD_GRAU_ESCOLARIDADE == 8) * ch.QT_ELEITORES
                    parts.append(ch.groupby(["SG_UF", "CD_MUNICIPIO"])[
                        ["QT_ELEITORES", "fem", "jov", "ido", "baixa", "sup"]].sum())
            print(f"  perfil {uf}")
    pd.concat(parts).groupby(level=[0, 1]).sum().reset_index().to_csv(dest, index=False)
    z.unlink()
    print(f"✓ {dest.name}")


def tse_resultados():
    d = RAW / "tse_resultados"
    d.mkdir(parents=True, exist_ok=True)
    e = ELEICAO_2026_T1
    (d / "mun-cm.json").write_bytes(get(f"{TSE_RES}/ele2026/{e}/config/mun-e00{e}-cm.json").content)
    for uf in ["br"] + [u.lower() for u in UFS] + ["zz"]:
        f = d / f"{uf}-c0001-e00{e}-u.json"
        if f.exists() and not FORCE:
            continue
        f.write_bytes(get(f"{TSE_RES}/ele2026/{e}/dados/{uf}/{uf}-c0001-e00{e}-u.json").content)
    print("✓ TSE divulgação (de-para + totais 1T26 por UF)")


def ibge_malhas():
    d = RAW / "ibge"
    d.mkdir(parents=True, exist_ok=True)
    base = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo%2Bjson&qualidade=minima"
    for nivel, nome in [("municipio", "malha_municipios.geojson"), ("UF", "malha_ufs.geojson")]:
        f = d / nome
        if not f.exists() or FORCE:
            f.write_bytes(get(f"{base}&intrarregiao={nivel}").content)
    f = d / "municipios.json"
    if not f.exists() or FORCE:
        f.write_bytes(get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios").content)
    print("✓ IBGE malhas e localidades")


# (nome, tabela, variáveis, período, classificações)  — consultas por UF (limite de valores do SIDRA)
SIDRA_QUERIES = [
    ("pop_dens", 4714, "93,614", "2022", ""),
    ("domicilios", 4712, "381", "2022", ""),
    ("urbana", 9923, "1000093", "2022", "/c1/1"),
    ("cor_raca", 9605, "1000093", "2022", "/c86/2777,2779"),
    ("alfabetizacao", 9543, "2513", "2022", "/c2/6794/c86/95251/c287/100362"),
    ("superior", 10061, "1002667", "2022", "/c1568/99713/c58/95253/c2/6794/c86/95251"),
    ("renda", 10295, "13431,13534", "2022", "/c2/6794/c86/95251/c58/95253"),
    ("religiao", 10198, "1000950", "2022", "/c133/95277,95263/c58/95253/c59/93024"),
    ("pib", 5938, "37", "2022", ""),
]


def sidra():
    d = RAW / "ibge" / "sidra"
    d.mkdir(parents=True, exist_ok=True)
    for nome, t, v, p, c in SIDRA_QUERIES:
        f = d / f"{nome}.csv"
        if f.exists() and not FORCE:
            print(f"= sidra {nome}")
            continue
        rows = []
        for uf, cod in UF_COD.items():
            js = get(f"{SIDRA}/t/{t}/n6/in%20n3%20{cod}/v/{v}/p/{p}{c}?formato=json").json()
            rows += js[1:]
        df = pd.DataFrame(rows)
        keep = ["D1C", "D1N", "D2C", "V"] + [k for k in df.columns if k.startswith("D") and k.endswith("C") and k not in ("D1C", "D2C", "D3C")]
        df[keep].to_csv(f, index=False)
        print(f"✓ sidra {nome} ({len(df)} linhas)")


def mds():
    d = RAW / "mds"
    d.mkdir(parents=True, exist_ok=True)
    campos = "codigo_ibge,anomes_s,qtd_familias_beneficiarias_bolsa_familia_i,qtd_pessoas_beneficiarias_bolsa_familia_i"
    # mês mais recente com dados de Bolsa Família para (quase) todos os municípios
    ym = pd.Timestamp.today()
    for _ in range(18):
        mes = ym.strftime("%Y%m")
        r = get(MDS, params={"q": "*:*", "fq": [f"anomes_s:{mes}", "qtd_familias_beneficiarias_bolsa_familia_i:[1 TO *]"],
                             "rows": 0, "wt": "json"}).json()
        if r["response"]["numFound"] > 5500:
            break
        ym -= pd.DateOffset(months=1)
    f = d / "bolsa_familia.csv"
    txt = get(MDS, params={"q": "*:*", "fq": f"anomes_s:{mes}", "fl": campos, "rows": 10000, "wt": "csv"}).text
    f.write_text(txt)
    print(f"✓ MDS Bolsa Família ({mes})")


if __name__ == "__main__":
    RAW.mkdir(exist_ok=True)
    for ano in (2022, 2026):
        tse_zip_member("detalhe_votacao_munzona", ano, f"_{ano}_BR.csv", RAW / "tse" / f"detalhe_votacao_munzona_{ano}_BR.csv")
        tse_zip_member("votacao_candidato_munzona", ano, f"_{ano}_BR.csv", RAW / "tse" / f"votacao_candidato_munzona_{ano}_BR.csv")
    tse_resultados()
    ibge_malhas()
    sidra()
    mds()
    if not SKIP_PERFIL:
        perfil_eleitorado(2026)
    (RAW / "extracao.json").write_text(json.dumps({"data_extracao": pd.Timestamp.now(tz="America/Sao_Paulo").isoformat(timespec="minutes")}))
    print("Pronto.")
