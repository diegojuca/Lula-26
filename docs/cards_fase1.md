# Cards compartilháveis — Fase 1 (investigação)

Data: 10/10/2026. Nada implementado. Legenda de verificação:
**✓ testado aqui** (baixei ou consultei a fonte neste ambiente) · **⚠ bloqueado aqui** (o domínio está fechado neste ambiente; a fonte existe, mas não verifiquei o dado) · **✗ não existe/inviável**.

Janelas fixas (vão para `config/janelas.json`): antes de Lula ≤2002 · Lula 1–2 2003–2010 · Dilma 2011–ago/2016 · Temer set/2016–2018 · Bolsonaro 2019–2022 · Lula 3 2023–último dado.
Correção monetária: IPCA (IBGE, SIDRA tabela 1737) **✓ testado**, com ano-base explícito no card (ex.: "R$ de ago/2026").

---

## (a) Matriz resumida: indicador × nível × fonte × cobertura por época

Épocas: **A** = antes (≤2002) · **L** = Lula 1–2 · **D** = Dilma · **TB** = Temer/Bolsonaro · **L3** = Lula 3.

### Chega a bairro
| Indicador | Fonte | Status | A | L | D | TB | L3 | Observação |
|---|---|---|---|---|---|---|---|---|
| Água por rede geral, esgoto, lixo coletado, energia (% domicílios) | IBGE, Censo 2000 e 2010 por setor (com código e nome de bairro) e 2022 por bairro | ✓ testado (PE) | 2000 | 2010 | — | 2022* | — | *2022 mistura D+TB+L3: **não usar** para atribuir. "Antes e depois" só 2000→2010. |
| Alfabetização (responsáveis pelo domicílio) | Censo 2000/2010 por setor/bairro | ✓ arquivos baixados; variável a mapear | 2000 | 2010 | — | — | — | Mesma definição nos dois Censos (responsável alfabetizado). |
| Renda no bairro ("abaixo de R$ X") | Censo por setor | ✗ inviável | | | | | | O setor só traz faixas em salários mínimos. Como o mínimo real subiu muito, a comparação engana. Com faixa fixa em reais, só no Atlas (UDH) ou município. |
| Pobreza, renda, mortalidade infantil por UDH (≈ bairro nas regiões metropolitanas) | Atlas Brasil (PNUD/IPEA/FJP), Censos 2000/2010 | ✓ site responde; extração a fazer | 2000 | 2010 | — | — | — | Linha de pobreza fixa (R$ de 2010). Vale só onde há UDH. |
| UBS (nome, bairro, coordenadas) | Min. Saúde, API dados abertos (UBS) | ✓ testado | — | — | — | — | hoje | Sem data de criação → **sem "Chegou com Lula"** para UBS. |
| Mais Médicos por UBS/bairro | Min. Saúde | ✗ | | | | | | Relatório por estabelecimento vazio na API, e a lista nominal não traz o estabelecimento. **Fica no município.** |
| SAMU, UPA, CEO com data de cadastro | CNES (API) | ✗/⚠ | | | | | | A API do CNES traz endereço sem bairro e sem data de criação. O CNES completo (DataSUS) está bloqueado aqui. |
| Campi de IF/universidades (ano de criação) | MEC / Plataforma Nilo Peçanha | ⚠ bloqueado (anti-robô) | | | | | | Sem verificação → card "Chegou com Lula" de campus **não sai** até termos a lista oficial. |
| Farmácia Popular (farmácias credenciadas) | Min. Saúde (S3 demas-dados-abertos) | ⚠ domínio bloqueado | | | | | | Libere `demas-dados-abertos.s3.amazonaws.com`. |
| MCMV (empreendimentos), Novo PAC (obras) | Min. Cidades / Casa Civil | ⚠ servidores não respondem | | | | | | Os servidores provavelmente recusam acessos de fora do Brasil. |

### Fica na cidade
| Indicador | Fonte | Status | A | L | D | TB | L3 | Observação |
|---|---|---|---|---|---|---|---|---|
| Bolsa Família (famílias, valor) mês a mês | MDS, MI Social | ✓ testado: Recife jan/2004 → set/2026 | — | 2004–10 | ✓ | ✓ (2021–22 = Auxílio Brasil, campos `pab_*`) | ✓ | Mesma métrica (famílias, valor real médio) nas três janelas. |
| Pé-de-Meia (parcelas, valor) | CGU, Portal da Transparência | ✓ testado | — | — | — | — | 2024+ | Só "Está aqui". |
| Mais Médicos (médicos ativos) | Min. Saúde, série histórica 2013→2026 | ✓ testado (Recife desde 29/11/2013) | — | — | ✓ | ✓ | ✓ | Programa da Dilma. Lula 1–2 não existe. "Três tempos" = Dilma × Temer/Bolsonaro × Lula 3, com a métrica médicos ativos em dezembro. |
| Cisternas entregues | MDS, MI Social | ✓ campos existem; série a validar | ? | ✓ | ✓ | ✓ | ✓ | Programa de origem mista (ASA/P1MC; lei de 2013) → **só "Está aqui"**, nunca "Lula fez". |
| Pobreza, extrema pobreza, renda, mortalidade infantil, IDHM | Atlas Brasil (Censos 2000/2010) | ✓ site responde | 2000 | 2010 | — | — | — | "Antes e depois" municipal com linha fixa em reais. |
| PIB municipal | IBGE, SIDRA 5938 (2002–2023) | ✓ testado | 2002 | ✓ | ✓ | ✓ | 2023 | Real pelo deflator/IPCA. Card só se não houver queda na janela. |
| Mortalidade infantil anual (SIM/SINASC) | DataSUS | ⚠ bloqueado | | | | | | A API da Saúde só tem microdados paginados, inviável. Use o Atlas (2000 × 2010). |
| Cobertura vacinal | PNI / DataSUS | ⚠ / parcial | | | | | | A API só tem doses de 2020+, sem denominador. Fora. |
| Empregos formais (RAIS/CAGED) | MTE (PDET) | ⚠ bloqueado | | | | | | Fora até liberar o acesso. |
| ProUni, matrículas (INEP), Pronaf (BCB/SICOR), PAA/PNAE (FNDE) | MEC/INEP, BCB, FNDE | ⚠ bloqueados | | | | | | Fora até liberar o acesso. |
| MCMV/Casa Verde e Amarela por ano de contratação | Min. Cidades | ⚠ | | | | | | Fora até liberar o acesso. |
| Transferências federais | CGU/Tesouro | ✓ parcial | | | | | | São repasses obrigatórios, não entregas. Fora dos cards. |

### UF e Brasil
| Indicador | Fonte | Status | Cobertura | Observação |
|---|---|---|---|---|
| Salário mínimo real (ganho por janela) | Valor legal do mínimo, deflacionado pelo IPCA (SIDRA 1737) | ✓ IPCA testado; os valores legais vêm das leis (Planalto ⚠ bloqueado) | 2002–2026 | Calculo eu mesmo; não depende do IPEA. O valor de 2026 precisa ser confirmado na lei. |
| Desemprego, renda média (PNAD Contínua) por UF | IBGE SIDRA | ✓ SIDRA responde | 2012+ | Não cobre Lula 1–2: só "Três tempos" a partir de Dilma. |
| Pobreza e extrema pobreza por UF | IBGE, Síntese de Indicadores Sociais (SIDRA) | ✓ SIDRA; tabela a confirmar | 2012+ | Idem. |
| Insegurança alimentar (EBIA) por UF | IBGE: PNAD 2004/2009/2013, POF 2017-18, PNAD Contínua 2023 | ✓ SIDRA; tabelas a confirmar | 2004, 2009, 2013, 2018, 2023 | Ótimo para "Três tempos" (2004→2013 queda, 2018 alta, 2023 queda). Os anos de pesquisa não coincidem com as janelas; o card informa os anos. |
| Mapa da Fome (FAO) | FAO, relatório SOFI | ⚠ bloqueado | 2014 (saída), 2022 (retorno, triênio 2019–21), 2025 (nova saída) | Conferir no relatório antes de publicar. |
| Dívida com o FMI e reservas | BCB / FMI | ⚠ bloqueado | Quitação antecipada em dez/2005 | Fato histórico; conferir o comunicado oficial (BCB/Fazenda) antes de publicar. |

**Resumo de (a)**
- **Bairro:** só Censo 2000→2010 (água, esgoto, lixo, energia, alfabetização) e UBS presentes hoje. Pobreza por "bairro" apenas via UDH do Atlas, nas regiões metropolitanas.
- **Cidade:** Bolsa Família (2004→hoje, as três épocas), Mais Médicos (2013→hoje), Pé-de-Meia, cisternas, Atlas 2000×2010 e PIB.
- **UF/Brasil:** salário mínimo real, PNAD (2012+), insegurança alimentar (2004–2023), Mapa da Fome e FMI.
- **Cobertura das três épocas na mesma métrica:**
  - Bolsa Família (cidade), Mais Médicos (cidade, sem Lula 1–2), insegurança alimentar (UF) e salário mínimo real (Brasil): **sim**.
  - Censo: só antes × Lula.

---

## (b) Correspondência de bairros (TSE × IBGE 2022), 27 capitais

Medida com o nome do bairro dos locais de votação (TSE 2026) normalizado (acentos, abreviações como "JD/VL/PQ/CJ") contra os bairros oficiais do Censo 2022, em % dos eleitores:

| Faixa | Capitais |
|---|---|
| ≥ 90% | Fortaleza 98,9 · Manaus 96,4 · Vitória 95,6 · Aracaju 95,3 · Belém 95,3 · Rio 94,9 · Porto Alegre 93,0 · Boa Vista 92,4 · Recife 91,3 |
| 80–90% | Natal 89,1 · Curitiba 89,1 · Salvador 88,9 · Maceió 85,4 · Macapá 82,8 |
| 60–80% | BH 79,8 · Florianópolis 75,2 · Teresina 73,8 · Porto Velho 71,4 · João Pessoa 70,3 · Cuiabá 64,7 |
| < 60% | Campo Grande 29,6 |
| **sem bairro oficial no IBGE** | São Paulo, Brasília, Goiânia, São Luís, Palmas, Rio Branco (0%) |

- Mediana entre as 21 capitais com bairro oficial: 89%.
- **Regra:** o card só fala "Na Várzea" se o bairro casar exatamente. Senão, o card sobe para a cidade.
- **Continuidade de bairro entre Censos:** o Recife tem os mesmos 94 bairros em 2000, 2010 e 2022, e a Várzea existe nos três (testado). Para outras cidades, o "Antes e depois" por bairro só sai se o bairro existir com o mesmo código e nome em 2000 e 2010; senão, sobe para a cidade.
- A tabela de normalização (sinônimos, abreviações e correções manuais) fica num arquivo `config/bairros_normalizacao.csv`.

---

## (c) Ficha de autoria (o que os cards podem dizer)

As normas abaixo vêm do meu conhecimento da legislação. O site do Planalto está **bloqueado aqui**, então todas ficam marcadas "conferir" até eu (ou você) abrir o link. Nenhum card de autoria sai antes dessa conferência.

| Programa | Criação | Governo | Norma de origem (conferir) | Antecessor | Situação por janela | O card pode dizer |
|---|---|---|---|---|---|---|
| Bolsa Família | out/2003 | Lula 1 | MP 132/2003 → Lei 10.836/2004 | Bolsa Escola (2001), Bolsa Alimentação (2001), Auxílio-Gás (2002), Cartão Alimentação (2003) | L: criado/ampliado · D: ampliado · T: mantido · B: substituído pelo Auxílio Brasil (Lei 14.284/2021) · L3: recriado (Lei 14.601/2023) | "criado em 2003, no governo Lula"; "recriado em 2023" |
| Fome Zero | jan/2003 | Lula 1 | estratégia de governo (sem lei única) | — | — | "lançado em 2003" (sem "programa") |
| PAA (compra da agricultura familiar) | 2003 | Lula 1 | Lei 10.696/2003, art. 19 | — | B: substituído pelo Alimenta Brasil (2021) · L3: retomado (Lei 14.628/2023) | criado e retomado por Lula |
| Luz para Todos | nov/2003 | Lula 1 | Decreto 4.873/2003 | Luz no Campo (1999–2002, FHC) | D: prorrogado · T: prorrogado (2018) · B: + "Mais Luz para a Amazônia" (2020) · L3: renovado (2023) | "criado em 2003, no governo Lula" (sem "primeiro"; houve antecessor) |
| Farmácia Popular | 2004 | Lula 1 | Lei 10.858/2004; Decreto 5.090/2004 | — | L: criado + "Aqui Tem" (2006) · T: rede própria fechada (2017) · L3: ampliado (2023) | criado por Lula; ampliação em 2023 |
| SAMU 192 | 2003–2004 | Lula 1 | Portaria GM/MS 1.864/2003; Decreto 5.055/2004 | — | contínuo | "criado no governo Lula" (o serviço local é operado pelo município ou estado → nunca "Lula fez o SAMU daqui") |
| Brasil Sorridente (CEOs) | 2004 | Lula 1 | Política Nacional de Saúde Bucal (2004) | — | contínuo | idem SAMU |
| UPA 24h | 2009 | Lula 2 | Portaria GM/MS 1.020/2009 | — | contínuo | idem; UPA é construída e operada por município ou estado com recurso federal |
| ProUni | 2004/2005 | Lula 1 | MP 213/2004 → Lei 11.096/2005 | — | contínuo | criado por Lula |
| REUNI / novas universidades | 2007 | Lula 2 | Decreto 6.096/2007 (+ leis de criação de cada universidade) | — | — | por universidade, com a lei de criação |
| Rede Federal / Institutos Federais | 2008 (expansão desde 2005) | Lula | Lei 11.892/2008; Lei 11.195/2005 | escolas técnicas federais/CEFETs (desde 1909) | campi novos em todas as janelas | só "campus aberto em AAAA, no governo X" com a data oficial do campus (fonte ⚠) |
| PNAE: 30% da agricultura familiar | 2009 | Lula 2 | Lei 11.947/2009 | PNAE existe desde 1955 | contínuo | "a regra dos 30% é de 2009, governo Lula" (nunca "Lula criou a merenda") |
| Minha Casa Minha Vida | mar/2009 | Lula 2 | MP 459/2009 → Lei 11.977/2009 | — | D: ampliado · T: mantido · B: substituído pelo Casa Verde e Amarela (Lei 14.118/2021) · L3: retomado (Lei 14.620/2023) | criado e retomado por Lula |
| Valorização do salário mínimo | 2007 (acordo) | Lula 2 | regra em lei: Lei 12.382/2011 (Dilma), Lei 13.152/2015 (Dilma) | — | B: sem regra de ganho real · L3: Lei 14.663/2023 | "política iniciada no governo Lula"; "retomada em 2023" |
| Mais Médicos | jul/2013 | **Dilma** | MP 621/2013 → Lei 12.871/2013 | — | B: substituído pelo Médicos pelo Brasil (Lei 13.958/2019) · L3: retomado (Lei 14.621/2023) | **"retomado em 2023, no governo Lula"**; nunca "criado por Lula" |
| Água para Todos / Cisternas | 2011 / 2013 (P1MC da ASA desde 2003 com apoio federal) | Dilma (lei) | Decreto 7.535/2011; Lei 12.873/2013 | P1MC (sociedade civil) | — | **sem autoria**; só "Está aqui" |
| Pronaf | 1996 | FHC | Decreto 1.946/1996 | — | ampliado em várias janelas | **sem autoria**; só "Três tempos" de crédito (fonte ⚠) |
| Auxílio Gás | 2021 | Bolsonaro/Congresso | Lei 14.237/2021 | Auxílio-Gás (2002) | — | **fora** |
| Pé-de-Meia | jan/2024 | Lula 3 | Lei 14.818/2024 | — | — | criado por Lula |
| Quitação antecipada da dívida com o FMI | dez/2005 | Lula 1 | ato do Tesouro/BCB (comunicado) | — | — | fato com data e fonte (⚠ conferir) |

---

## (d) Modelos de card (22)

Variáveis entre `{ }`. "Nível" = nível mínimo do dado. O lugar no texto segue o nível do dado ("Na {bairro}" / "Em {cidade}" / "Em {UF}" / "No Brasil").

**Tipo 1 — Está aqui**
1. **BF-HOJE**: "{Lugar}: {n} famílias recebem o Bolsa Família." · Cidade · L3 · MDS, {mês/ano} · Mínimo n ≥ 100; dado ≤ 3 meses.
2. **BF-VALOR**: "{Lugar}: o Bolsa Família pagou {R$} às famílias daqui só em {mês/ano}." · Cidade · L3 · MDS · Mínimo R$ 100 mil no mês.
3. **PDM-HOJE**: "{Lugar}: estudantes do ensino médio receberam {n} parcelas do Pé-de-Meia em {mês/ano}." · Cidade · L3 · CGU · Mínimo n ≥ 50.
4. **MM-HOJE**: "{Lugar}: {n} médicos do Mais Médicos atendem hoje." · Cidade · L3 · Min. Saúde, {data} · Mínimo n ≥ 3.
5. **UBS-BAIRRO**: "{Bairro}: {n} unidades básicas de saúde do SUS atendem o bairro." · Bairro · hoje · Min. Saúde/CNES · Mínimo n ≥ 2. Não atribui a governo.
6. **CISTERNAS**: "{Lugar}: {n} cisternas entregues pelo programa federal." · Cidade · série · MDS · Mínimo n ≥ 50. Sem autoria.

**Tipo 2 — Chegou com Lula** (cada um sai só depois de a norma estar conferida)
7. **BF-ORIGEM**: "O Bolsa Família, que hoje atende {n} famílias em {cidade}, foi criado em 2003, no governo Lula." · Cidade · ficha.
8. **MCMV-ORIGEM**: "O Minha Casa Minha Vida foi criado em 2009 e retomado em 2023, nos governos Lula." · Brasil · ficha. (Versão local só com dado de contratação do Min. Cidades ⚠.)
9. **MM-RETOMADA**: "O Mais Médicos foi retomado em 2023. Hoje são {n} médicos do programa em {cidade}." · Cidade · ficha (criado por Dilma; o card diz "retomado").
10. **CAMPUS**: "O campus {nome} do IF em {cidade} foi aberto em {ano}, no governo Lula." · Endereço · fonte ⚠ · só com data oficial MEC.

**Tipo 3 — Antes e depois** (janela fixa 2000→2010 = Censos; o card diz "entre 2000 e 2010")
11. **ESGOTO-BAIRRO**: "{Bairro}: os domicílios com esgoto por rede geral passaram de {a}% para {b}% entre 2000 e 2010, no governo Lula." · Bairro (Censo) · Mínimo +3 pp e base ≥ 200 domicílios.
12. **AGUA-BAIRRO**: idem, água por rede geral. Mesmas regras.
13. **LIXO-BAIRRO**: idem, lixo coletado. Mesmas regras.
14. **POBREZA-MUN**: "{Cidade}: a parcela de pessoas em situação de pobreza caiu de {a}% para {b}% entre 2000 e 2010, no governo Lula." · Cidade/UDH (Atlas) · linha fixa do Atlas (R$ 140 de 2010) · Mínimo −3 pp.
15. **MORT-INF-MUN**: "{Cidade}: a mortalidade infantil caiu de {a} para {b} por mil nascidos vivos entre 2000 e 2010." · Cidade (Atlas) · Mínimo −2 por mil.
16. **ALFAB-BAIRRO**: "{Bairro}: os responsáveis por domicílio que sabem ler passaram de {a}% para {b}% entre 2000 e 2010." · Bairro · Mínimo +2 pp.

**Tipo 4 — Três tempos** (mesma métrica; o card sai só se o valor de Lula 1–2 e o de Lula 3 forem ambos melhores que o de Temer/Bolsonaro)
17. **BF-3T**: "Famílias atendidas pelo Bolsa Família em {cidade}, média anual: Lula 1–2: {x} · Temer/Bolsonaro: {y} · Lula 3: {z}." · Cidade · MDS. Alternativa: valor médio real por família (R$ de {mês/ano}). O período 2021–22 aparece com o rótulo "Auxílio Brasil". Dilma vai numa nota no rodapé do card ("Dilma: {d}"), para não sumir.
18. **MM-3T**: "Médicos do Mais Médicos em {cidade}, dezembro de cada ano: Dilma {d} · Temer/Bolsonaro {y} · Lula 3 {z}." · Cidade · Min. Saúde. Sem coluna Lula 1–2 (o programa não existia).
19. **SM-3T**: "Ganho real do salário mínimo: Lula 1–2 +{x}% · Temer/Bolsonaro +{y}% · Lula 3 +{z}%." · Brasil · valor legal + IPCA. Uma nota no rodapé mostra Dilma.
20. **FOME-3T-UF**: "Domicílios com fome (insegurança alimentar grave) em {UF}: {2013}: {a}% · {2018}: {b}% · {2023}: {c}%." · UF · IBGE · O card informa os anos de pesquisa, sem nomear governos no número.

**Tipo 5 — O Brasil que mudou** (moldura nacional quando faltar dado local)
21. **FMI**: "Em dezembro de 2005, o Brasil quitou antecipadamente a dívida com o FMI, no governo Lula." · Brasil · fonte ⚠ conferir.
22. **MAPA-FOME**: "O Brasil saiu do Mapa da Fome da ONU em 2014, voltou em 2022 e saiu de novo em 2025." · Brasil · FAO/SOFI ⚠ conferir.

**Bloqueio automático (todos os modelos)**
- O card não sai se:
  - o número estiver abaixo do mínimo do modelo;
  - houver piora na janela ou o contraste dos três tempos não for verdadeiro;
  - o dado for mais velho que o limite do modelo;
  - o nível do dado for mais amplo que o do texto;
  - a autoria não estiver conferida;
  - o responsável estiver vazio.
- Arredondamento sempre para baixo nos números de entrega.

---

## (e) Biblioteca de fechos (para aprovar)

| Código | Texto | Tipo | Permitido em |
|---|---|---|---|
| F1 | "Com Lula, continua e cresce." | afirmativo | 1, 3, 4, 5 (programa ativo hoje) |
| F2 | "Foi o Lula que fez." | afirmativo | só 2, quando a ficha diz "criado por Lula" (BF, MCMV, Farmácia Popular, Luz para Todos, ProUni, PAA, Pé-de-Meia, campus com data) |
| F3 | "Foi o Lula que trouxe de volta." | afirmativo | só "retomado" (Mais Médicos, MCMV 2023, Bolsa Família 2023, PAA) |
| F4 | "Isso é o Brasil que dá certo." | afirmativo | 3, 4, 5 |
| F5 | "Conta pra quem ainda não sabe." | afirmativo (chamada) | todos |
| R1 | "Sem Lula, isso pode acabar." | **risco: desligado** | 1, 2 (programas que já foram substituídos ou cortados antes: BF, MM, MCMV, PAA, Farmácia Popular) |
| R2 | "Já tentaram acabar uma vez." | **risco: desligado** | só programas com substituição documentada na ficha (BF→Auxílio Brasil; MM→Médicos pelo Brasil; MCMV→Casa Verde e Amarela; PAA→Alimenta Brasil) |

A chave `fechos_de_risco: false` fica em `config/cards.json`.

---

## Para liberar mais dados (opcional)
Domínios fechados neste ambiente e o que destravam:

| Domínio | Destrava |
|---|---|
| `www.planalto.gov.br` | conferir as normas da ficha |
| `api.bcb.gov.br` | FMI/reservas, Pronaf |
| `www.ipeadata.gov.br` | séries históricas |
| `download.inep.gov.br` | matrículas no ensino superior |
| `pdet.mte.gov.br` | RAIS/CAGED |
| `demas-dados-abertos.s3.amazonaws.com` | Farmácia Popular |
| `www.fao.org` | Mapa da Fome |
| `cnes.datasus.gov.br` / `datasus.saude.gov.br` | CNES com data de criação; SIM/SINASC anual |
| `plataformanilopecanha.mec.gov.br` | campi dos IFs |

Mesmo liberando, a página da MEC usa uma verificação anti-robô e pode continuar inacessível.
