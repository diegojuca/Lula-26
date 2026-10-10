# Cenário Presidencial 2026 — 2T22 → 1T26 (MVP)

Painel Tá Dito de cenário estratégico eleitoral: **onde e como Lula perdeu (ou ganhou) votos** entre o
**2º turno de 2022 (2T22)** e o **1º turno de 2026 (1T26, 04/10/2026)**, cruzado com indicadores
socioeconômicos, para apontar territórios estratégicos para o 2º turno (25/10/2026).

O MVP é independente: só usa fontes públicas, sem dependências de máquina local, sem segredos e sem CDN.
O painel funciona offline.

## Como abrir

| Onde | Como |
|---|---|
| Celular / qualquer navegador | Abra `painel/painel_standalone.html`, um arquivo único (~5,6 MB) com dados embutidos. |
| Computador (versão que lê `data/`) | `python -m http.server 8000` na raiz → `http://localhost:8000/painel/` |

## Estrutura

```
scripts/01_download.py    baixa as fontes públicas para raw/ (não versionado)
scripts/02_build.py       agrega, calcula métricas, valida contra o TSE e gera data/*.json
scripts/03_standalone.py  embute data/*.json no painel → painel/painel_standalone.html
data/                     JSON pré-agregados (municípios, UFs, regiões, meta, malhas) + validacao.csv
painel/index.html         painel estático, mobile first (lê ../data/*.json)
```

## Reexecutar

```bash
pip install -r requirements.txt
python scripts/01_download.py      # ~1,5 GB de download do TSE; extrai só o necessário e apaga os zips
python scripts/02_build.py         # falha (assert) se qualquer total não bater com o TSE
python scripts/03_standalone.py
```
`01_download.py --force` rebaixa tudo, por exemplo quando o TSE atualizar a totalização do 1T26.

## Fontes

| Fonte | Uso | Ciclo | Status |
|---|---|---|---|
| TSE dados abertos — `detalhe_votacao_munzona` e `votacao_candidato_munzona` (cargo Presidente, arquivo `_BR`) | aptos, comparecimento, abstenção, brancos, nulos, votos por candidato | 2022 (1T e 2T), 2026 (1T) | oficial; 1T26 gerado em 09/10/2026, **sujeito a atualização** |
| TSE divulgação (`resultados.tse.jus.br`, eleição 6257) | conferência por UF do 1T26 e **de-para oficial TSE × IBGE** (`mun-e006257-cm.json`, campo `cdi`) | 2026 | oficial |
| TSE `perfil_eleitorado_2026` | % feminino, 16–24, 60+, escolaridade do eleitorado | 07/2026 | oficial |
| IBGE SIDRA — Censo 2022 (tabelas 4714, 4712, 9923, 9605, 9543, 10061, 10295, 10198) | população, densidade, urbanização, cor/raça, alfabetização, superior completo, renda domiciliar per capita, religião | 2022 | oficial, **defasado** |
| IBGE SIDRA 5938 — PIB dos Municípios | PIB per capita (PIB 2022 ÷ população do Censo 2022) | 2022 | oficial, **defasado** |
| MDS — MI Social (`aplicacoes.mds.gov.br/sagi/servicos/misocial`) | pessoas e famílias no Bolsa Família | 09/2026 | oficial |
| IBGE — API de malhas v3 (qualidade mínima) | mapas de municípios e UFs | 2022 | oficial |

Domínios bloqueados neste ambiente, nenhum deles necessário: `aplicacoes.cidadania.gov.br` (VIS Data do MDS),
`portaldatransparencia.gov.br`, `basedosdados.org`, `raw.githubusercontent.com`, `ipeadata.gov.br` e os CDNs
(cdnjs, jsdelivr, unpkg). Por isso os gráficos usam um módulo SVG próprio, sem d3.

## Métricas (resumo; as fórmulas completas estão na aba "Regras e fontes" do painel)

- **Penetração** = votos ÷ eleitorado apto do pleito. É a métrica principal de variação, porque não é distorcida pelo comparecimento.
- **Adversário principal**: Flávio Bolsonaro (PL), 1º colocado no 1T26, comparado a Jair Bolsonaro (PL) no 2T22.
- **Saldo** = Lula − adversário, em votos e em pp dos válidos. A situação é "virou contra", "encolheu", "aumentou" ou "virou a favor".
- **Abstenção histórica** = média ponderada de 1T22 e 2T22. É o único uso do 1T22. **Abstenção excedente** = max(0, abst% 1T26 − histórica) × aptos 1T26.
- **Para onde foi o voto perdido**: é uma identidade contábil em frações do eleitorado (abstenção + brancos/nulos + Lula + adversário + terceiros = 100%). Pela identidade, −Δpen(Lula) = Δabstenção + Δbrancos/nulos + terceiros + Δpen(adversário). O resultado é escalado ao eleitorado de 2026. É saldo agregado, **nunca migração individual**.
- **Estoque em disputa** = terceiros + brancos/nulos + abstenção excedente (1T26). **Déficit** = adversário − Lula. A virada é aritmeticamente possível quando o estoque supera o déficit.
- **Potencial de ganho** = max(0, −Δpenetração) × aptos 1T26 + abstenção excedente × Lula % válidos 2T22.

### Segmentos (aplicados nesta ordem; os parâmetros ficam no topo de `02_build.py`)
"Reduto" significa Lula ≥ 55% dos válidos no 2T22.

| Segmento | Regra | Municípios |
|---|---|---:|
| Reconquista | reduto e Δ penetração ≤ −7 pp (Brasil: −4,6 pp) | 677 |
| Mobilização | reduto e (abstenção 1T26 ≥ 25% ou ≥ histórica + 2 pp) | 295 |
| Disputa | Lula 45–55% no 2T22 e eleitorado ≥ 50 mil | 106 |
| Consolidado (contexto) | demais redutos | 1.689 |
| Equilíbrio, pequeno porte (contexto) | 45–55% com eleitorado < 50 mil | 902 |
| Adverso (contexto) | Lula < 45% no 2T22 | 1.900 |

## Validação contra o TSE

- **1T26**: as somas municipais deste repositório foram comparadas com a divulgação oficial do TSE
  (`resultados.tse.jus.br`, arquivos `<uf>-c0001-e006257-u.json`), para Lula, Flávio e votos válidos, em todas as UFs, no exterior e no Brasil.
- **2T22**: o total Brasil bate com o resultado oficial (Lula 60.345.999 e Bolsonaro 58.206.354). Por UF, Lula + Bolsonaro = votos válidos do arquivo de detalhe.
  A divulgação de 2022 não está mais no ar em `resultados.tse.jus.br`, por isso não houve conferência por UF contra ela.
- O `02_build.py` aborta se qualquer linha divergir. Resultado: **todas as 29 linhas conferem.**

| UF | Lula 1T26 (painel) | Lula 1T26 (TSE) | Flávio 1T26 (painel) | Flávio 1T26 (TSE) | Válidos 1T26 (painel = TSE) | Lula 2T22 | Bolsonaro 2T22 | Lula+Bolsonaro = válidos 2T22 | OK |
|---|---:|---:|---:|---:|---:|---:|---:|:-:|:-:|
| AC | 134.770 | 134.770 | 302.807 | 302.807 | 469.066 | 121.566 | 287.750 | ✓ | ✓ |
| AL | 995.459 | 995.459 | 735.718 | 735.718 | 1.818.856 | 976.831 | 687.827 | ✓ | ✓ |
| AM | 1.046.996 | 1.046.996 | 976.764 | 976.764 | 2.170.763 | 1.004.991 | 961.741 | ✓ | ✓ |
| AP | 212.503 | 212.503 | 212.278 | 212.278 | 464.858 | 189.918 | 200.547 | ✓ | ✓ |
| BA | 5.664.771 | 5.664.771 | 2.442.585 | 2.442.585 | 8.560.291 | 6.097.815 | 2.357.028 | ✓ | ✓ |
| CE | 3.555.263 | 3.555.263 | 1.756.850 | 1.756.850 | 5.617.814 | 3.807.891 | 1.634.477 | ✓ | ✓ |
| DF | 675.627 | 675.627 | 909.616 | 909.616 | 1.772.808 | 729.295 | 1.041.331 | ✓ | ✓ |
| ES | 850.028 | 850.028 | 1.233.194 | 1.233.194 | 2.251.078 | 926.767 | 1.282.145 | ✓ | ✓ |
| GO | 1.188.880 | 1.188.880 | 2.051.888 | 2.051.888 | 3.827.823 | 1.542.115 | 2.193.041 | ✓ | ✓ |
| MA | 2.566.301 | 2.566.301 | 1.239.040 | 1.239.040 | 4.010.439 | 2.668.425 | 1.082.749 | ✓ | ✓ |
| MG | 5.188.936 | 5.188.936 | 5.777.548 | 5.777.548 | 11.976.235 | 6.190.960 | 6.141.310 | ✓ | ✓ |
| MS | 516.855 | 516.855 | 873.351 | 873.351 | 1.490.278 | 599.547 | 880.606 | ✓ | ✓ |
| MT | 581.681 | 581.681 | 1.298.581 | 1.298.581 | 1.993.288 | 652.786 | 1.216.730 | ✓ | ✓ |
| PA | 2.427.237 | 2.427.237 | 2.163.957 | 2.163.957 | 4.863.172 | 2.509.084 | 2.073.895 | ✓ | ✓ |
| PB | 1.541.127 | 1.541.127 | 831.377 | 831.377 | 2.513.747 | 1.601.953 | 802.502 | ✓ | ✓ |
| PE | 3.553.971 | 3.553.971 | 1.738.043 | 1.738.043 | 5.601.017 | 3.640.933 | 1.798.832 | ✓ | ✓ |
| PI | 1.523.710 | 1.523.710 | 517.028 | 517.028 | 2.146.394 | 1.551.383 | 467.065 | ✓ | ✓ |
| PR | 2.054.597 | 2.054.597 | 3.945.345 | 3.945.345 | 6.585.243 | 2.506.605 | 4.159.343 | ✓ | ✓ |
| RJ | 3.693.021 | 3.693.021 | 4.966.844 | 4.966.844 | 9.369.700 | 4.156.217 | 5.403.894 | ✓ | ✓ |
| RN | 1.237.963 | 1.237.963 | 720.493 | 720.493 | 2.071.898 | 1.326.785 | 711.381 | ✓ | ✓ |
| RO | 250.667 | 250.667 | 652.988 | 652.988 | 968.059 | 262.904 | 633.236 | ✓ | ✓ |
| RR | 74.420 | 74.420 | 231.322 | 231.322 | 325.545 | 67.128 | 213.518 | ✓ | ✓ |
| RS | 2.294.759 | 2.294.759 | 3.573.783 | 3.573.783 | 6.423.046 | 2.891.851 | 3.733.185 | ✓ | ✓ |
| SC | 1.127.168 | 1.127.168 | 3.000.020 | 3.000.020 | 4.500.897 | 1.351.918 | 3.047.630 | ✓ | ✓ |
| SE | 856.019 | 856.019 | 417.839 | 417.839 | 1.364.196 | 862.951 | 421.086 | ✓ | ✓ |
| SP | 9.505.413 | 9.505.413 | 12.922.023 | 12.922.023 | 24.882.948 | 11.519.882 | 14.216.587 | ✓ | ✓ |
| TO | 404.009 | 404.009 | 469.321 | 469.321 | 930.447 | 434.593 | 411.654 | ✓ | ✓ |
| ZZ | 157.387 | 157.387 | 143.900 | 143.900 | 330.882 | 152.905 | 145.264 | ✓ | ✓ |
| BR | 53.879.538 | 53.879.538 | 56.104.503 | 56.104.503 | 119.300.788 | 60.345.999 | 58.206.354 | ✓ | ✓ |

## Limitações conhecidas

- O 1T26 é a totalização oficial do TSE de 09/10/2026 e pode mudar (recontagens, decisões judiciais). Basta reexecutar os scripts.
- Comparar o 2T22 (dois candidatos) com o 1T26 (12 candidatos) é uma premissa analítica (polarização). Parte da "perda" é voto em terceiros, que fica explícito na decomposição e no estoque.
- O socioeconômico vem do Censo 2022 e do PIB 2022 (defasados). O IDHM (2010) não foi incluído.
- Boa Esperança do Norte (MT), criado depois de 2022, aparece somado a Sorriso e Nova Ubiratã (área comparável). O exterior entra só nos totais Brasil.
- Todas as associações são **territoriais** (nível município). Nada permite inferir comportamento individual nem causalidade.
- As malhas usam a qualidade "mínima" do IBGE, com coordenadas arredondadas (~100 m), suficiente para leitura em tela.

## Integração (segunda-feira)

- Base Eleitoral: trocar `01_download.py` pela leitura do DuckDB local. `02_build.py` só precisa dos mesmos campos agregados.
- `build_protegido.py`, KV e FTP: publicar `painel/` e `data/` no padrão Tá Dito. O painel é estático e não tem dependências externas.
