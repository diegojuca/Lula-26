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
| Disputa | Lula 45–55% no 2T22, de qualquer tamanho (até 14/10/2026 exigia eleitorado ≥ 50 mil) | 1.008 |
| Consolidado (contexto) | demais redutos | 1.689 |
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

---

# Versão pública v2 — "Vamos virar juntos / Onde seu voto vira mais votos"

Material de apoio da militância: **não é material oficial da campanha**. O mesmo pipeline gera dois produtos, e a versão de análise não muda.

**Antes de compartilhar o link**: preencha `MARCA.responsavel` em `painel_publico/template.html` e rode `python scripts/04_publico.py` (propaganda anônima na internet é vedada).

## Como gerar
```bash
python scripts/05_secoes.py         # votação de presidente por local (TSE, ~850 MB de download, ~2 min)
python scripts/06_bolsa_familia.py  # Bolsa Família mês a mês por município (MDS MI Social, 03/2023 até o último mês)
python scripts/07_federal.py        # Pé-de-Meia (CGU, último mês) e Mais Médicos (Saúde) por município
python scripts/04_publico.py        # página + arquivos sob demanda; confere a soma dos locais com a análise
```

## O que a página mostra
- **Cidade**: ação (Levar para votar / Conversar com quem mudou / Disputar bairro a bairro, as mesmas regras de segmento da análise), votos em jogo e Lula % válidos 2T22 → 1T26.
- **Onde agir**: todos os locais de votação, ordenados por prioridade (votos de penetração perdidos + abstenção excedente × % de Lula, a mesma fórmula do "potencial" da análise), com nome, endereço, bairro, variação de Lula, abstenção e votos em jogo. A ação do local usa as mesmas regras, aplicadas ao local.
  - Cidades com **200 mil eleitores ou mais**: primeiro os bairros (agregando os locais), depois os locais de cada bairro.
  - Locais com **menos de 300 eleitores**: "amostra pequena", sem percentuais e sem ação.
  - Locais sem correspondente comparável em 2022 (número diferente, ou eleitorado que mudou mais que 0,5x–2x): "local novo", só com 1T26.
- **A cidade**: população, renda média por pessoa, % da população no Bolsa Família, % urbana, faixas etárias e escolaridade do eleitorado, cada um comparado com a média do estado (diferença menor que 5% conta como "na média"). Sem religião e sem raça/cor.
- **Governo federal** (só programas federais com dado oficial por município; valores em reais truncados):
  - Bolsa Família (MDS, MI Social): famílias, pessoas, valor pago no mês e valor pago acumulado desde 03/2023.
  - Pé-de-Meia (Portal da Transparência/CGU, último mês publicado, 06/2026): parcelas pagas e valor pago. Os pagamentos a menores de 18 anos vêm anonimizados, então a página conta **parcelas**, não estudantes. O script lê só as colunas de município e valor e apaga o arquivo bruto.
  - Mais Médicos (Ministério da Saúde, API de Dados Abertos): vagas ocupadas (médicos atuando) no município, com a data de referência da fonte.
- **"Nas cidades pequenas, o voto mudou de lado"**: as cidades com até 50 mil eleitores concentram 71% da piora do saldo de Lula sobre o adversário (−3,1 mi de −4,4 mi). A lista "Onde mais conta" tem filtro por porte; no filtro "Pequenas", ordena por votos perdidos.

## Tamanho
- `painel_publico/index.html`: 440 KB (163 KB comprimido), com o índice de cidades embutido.
- `painel_publico/dados/*.json`: 40 arquivos carregados quando a pessoa escolhe a cidade, cada um com até ~500 KB (≤ ~165 KB comprimido). São um por UF, UFs grandes divididas em partes, e São Paulo e Rio capitais em arquivo próprio. Total de 11,9 MB.

## Ficou de fora
- **Farmácia Popular**: os arquivos ficam em `demas-dados-abertos.s3.amazonaws.com`, ainda bloqueado neste ambiente.
- **Minha Casa Minha Vida e Novo PAC**: `dados.cidades.gov.br` e `novopac.casacivil.gov.br` não respondem a este ambiente (provavelmente bloqueiam acessos de fora do Brasil). Alternativa: a API do dados.gov.br, com chave gratuita guardada em variável do ambiente.
- **Auxílio Gás**: o link de download do Portal da Transparência devolve erro 500.
- **Transferências constitucionais (FPM etc.)**: são repasses obrigatórios, não entregas de programa, então ficaram de fora para não atribuir ao governo algo automático.
- **BPC**: o MI Social mostra o mesmo número em todos os meses, então não é confiável.
- **Perfil por bairro**: exigiria cruzar os locais com os setores censitários do Censo 2022.

## Conferências
Soma dos locais = município da análise (aptos, Lula e adversário 1T26) **em todas as 5.569 cidades** (verificação automática no `04_publico.py`).

Locais de votação, recalculados direto dos arquivos brutos do TSE por seção:

| Cidade | Local | Aptos 1T26 | Lula 2T22 | Lula 1T26 | Lula % válidos | Abstenção | OK |
|---|---|---:|---:|---:|---|---:|:-:|
| São Paulo (SP) | EE. Washington Alves Natel | 9.840 | 4.948 | 3.996 | 68,1% → 58,6% | 25,0% | ✓ |
| São Paulo (SP) | Amelia Kerr Nogueira Profa - EE | 9.327 | 5.680 | 4.121 | 73,0% → 64,6% | 25,8% | ✓ |
| Salvador (BA) | Colégio Rotary | 14.943 | 10.248 | 7.250 | 74,3% → 68,6% | 24,4% | ✓ |
| Salvador (BA) | Centro Educacional Nossa Senhora do Resgate | 3.760 | 3.458 | 1.708 | 64,8% → 57,8% | 18,0% | ✓ |
| Feira de Santana (BA) | Escola Estadual Carolina Maria de Jesus | 7.440 | 3.639 | 3.250 | 66,5% → 58,5% | 19,2% | ✓ |
| Feira de Santana (BA) | Colégio Estadual Edith Machado Boaventura | 8.087 | 4.300 | 3.856 | 70,2% → 62,6% | 18,8% | ✓ |
| Itabuna (BA) | Grupo Escolar Mun. Prof. Everaldo Cardoso | 3.550 | 1.490 | 1.354 | 58,0% → 56,0% | 25,2% | ✓ |
| Itabuna (BA) | Colégio Batista de Itabuna | 5.195 | 2.246 | 2.007 | 53,3% → 48,8% | 17,8% | ✓ |
| Boa Esperança do Sul (SP) | EE. Coronel Marcelino Braga | 3.293 | 1.418 | 977 | 55,4% → 41,1% | 22,8% | ✓ |
| Boa Esperança do Sul (SP) | EMEF. Anna Maria Mazzali | 2.989 | 1.417 | 976 | 59,6% → 45,0% | 20,8% | ✓ |

Bolsa Família, consultado de novo no MI Social (MDS):

| Item | Página | Fonte | OK |
|---|---:|---:|:-:|
| Itabuna: famílias, set/2026 | 22.171 | 22.171 | ✓ |
| Salvador: valor pago, set/2026 | R$ 190.400.528 | R$ 190.400.528 | ✓ |
| São Paulo: valor pago, mar/2023–set/2026 (43 meses) | R$ 19.576.961.312 | R$ 19.576.961.312 | ✓ |
| Itabuna: Pé-de-Meia, parcelas e valor, jun/2026 (recontagem do CSV da CGU) | 4.137 / R$ 827.875,00 | 4.137 / R$ 827.875,00 | ✓ |
| Feira de Santana: Mais Médicos, vagas ocupadas (09/10/2026) | 46 | 46 | ✓ |
