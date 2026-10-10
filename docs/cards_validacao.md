# Validação dos cards (antes de publicar)

Cada lugar lista os cards **gerados** (texto final, valor, fecho, período, fonte com link) e os **bloqueados** com o motivo.
Os cards de estado e Brasil aparecem para todos os lugares e estão no fim.

## Várzea (Recife, PE) — bairro

**Cards do bairro**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| — | | | nenhum card de bairro | | | |

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| MM-HOJE | cidade | 292 | Recife (PE): 292 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| MM-RETOMADA | cidade | 2023 | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 292 médicos do programa em Recife. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| BF-HOJE | cidade | 139.327 | Recife (PE): 139.327 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 139.327 famílias em Recife, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| POBREZA-MUN | cidade | 25,7% → 13,2% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Recife caiu de 25,7% para 13,2%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [86389, 210.24], "temer_bolsonaro": [102428, 247.88], "lula3": [143647, 722.95]} |
| CENSO-BAIRRO-LIXO | bairro | piora ou avanço pequeno | [98.4, 98.5] |

## Bom Jardim (Fortaleza, CE) — bairro

**Cards do bairro**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| CENSO-BAIRRO | bairro | 10% → 41% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Bom Jardim (Fortaleza) passaram de 10% para 41%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| BF-HOJE | cidade | 303.317 | Fortaleza (CE): 303.317 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 303.317 famílias em Fortaleza, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| POBREZA-MUN | cidade | 27,5% → 12,1% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Fortaleza caiu de 27,5% para 12,1%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| MORT-INF-MUN | cidade | 34,6 → 15,8 | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Fortaleza caiu de 34,6 para 15,8. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| PDM-HOJE | cidade | 69.899 | Fortaleza (CE): estudantes daqui receberam 69.899 parcelas do Pé-de-Meia em jun/2026. | Foi o Lula que fez. | jun/2026 | [CGU, Portal da Transparência](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [126449, 198.78], "temer_bolsonaro": [221071, 294.8], "lula3": [323335, 717.27]} |

## Guamá (Belém, PA) — bairro

**Cards do bairro**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| CENSO-BAIRRO | bairro | 11% → 38% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Guamá (Belém) passaram de 11% para 38%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| MM-HOJE | cidade | 199 | Belém (PA): 199 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| MM-RETOMADA | cidade | 2023 | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 199 médicos do programa em Belém. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| BF-HOJE | cidade | 147.006 | Belém (PA): 147.006 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 147.006 famílias em Belém, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| POBREZA-MUN | cidade | 24,4% → 13,0% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Belém caiu de 24,4% para 13,0%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [54965, 222.56], "temer_bolsonaro": [124666, 278.25], "lula3": [173302, 715.58]} |
| CENSO-BAIRRO-AGUA | bairro | piora ou avanço pequeno | [95.7, 92.9] |
| CENSO-BAIRRO-LIXO | bairro | piora ou avanço pequeno | [97.4, 96.2] |

## Exu (PE) — cidade pequena do semiárido

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| BF-HOJE | cidade | 7.939 | Exu (PE): 7.939 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 7.939 famílias em Exu, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| MM-HOJE | cidade | 4 | Exu (PE): 4 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| MM-RETOMADA | cidade | 2023 | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 4 médicos do programa em Exu. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| MORT-INF-MUN | cidade | 62,1 → 22,7 | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Exu caiu de 62,1 para 22,7. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [4207, 243.4], "temer_bolsonaro": [6758, 381.57], "lula3": [8263, 738.82]} |

## Canudos (BA) — cidade pequena do semiárido

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| MM-HOJE | cidade | 6 | Canudos (BA): 6 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| MM-RETOMADA | cidade | 2023 | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 6 médicos do programa em Canudos. | Foi o Lula que trouxe de volta. | 09/10/2026 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| BF-HOJE | cidade | 3.901 | Canudos (BA): 3.901 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 3.901 famílias em Canudos, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| CISTERNAS | cidade | 1.380 | Canudos (BA): 1.380 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | Conta pra quem ainda não sabe. | até abr/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [1954, 232.21], "temer_bolsonaro": [3361, 346.41], "lula3": [3948, 738.0]} |

## Porto Alegre (RS) — capital do Sul

**Cards da cidade**

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| BF-HOJE | cidade | 80.592 | Porto Alegre (RS): 80.592 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| BF-ORIGEM | cidade | 2003 | O Bolsa Família, que hoje atende 80.592 famílias em Porto Alegre, foi criado em 2003, no governo Lula. | Foi o Lula que fez. | 2003; set/2026 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| POBREZA-MUN | cidade | 8,5% → 3,8% | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Porto Alegre caiu de 8,5% para 3,8%. | Isso é o Brasil que dá certo. | 2000 e 2010 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| PDM-HOJE | cidade | 14.661 | Porto Alegre (RS): estudantes daqui receberam 14.661 parcelas do Pé-de-Meia em jun/2026. | Foi o Lula que fez. | jun/2026 | [CGU, Portal da Transparência](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| BF-3T | cidade | contraste não verdadeiro: famílias atendidas em Temer/Bolsonaro maiores que numa janela Lula | {"lula12": [31579, 211.51], "temer_bolsonaro": [52496, 332.86], "lula3": [83797, 722.27]} |

## Estado: PE

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| BF-HOJE | uf | 1.504.146 | Em Pernambuco, 1.504.146 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| MM-HOJE | uf | 1.643 | Em Pernambuco, 1.643 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 2026-10-09 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| FOME-UF-L3 | uf | piora ou queda pequena | [6.6, 8.5] |

## Estado: SP

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| BF-HOJE | uf | 2.321.827 | Em São Paulo, 2.321.827 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| MM-HOJE | uf | 3.394 | Em São Paulo, 3.394 médicos do Mais Médicos atendem hoje. | Foi o Lula que trouxe de volta. | 2026-10-09 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| FOME-UF-L3 | uf | piora ou queda pequena | [8.5, 8.7] |

## Brasil

| Modelo | Nível | Valor | Texto | Fecho | Período | Fonte |
|---|---|---|---|---|---|---|
| FOME-BR | brasil | 6,9% → 5,0% | No Brasil, os domicílios em insegurança alimentar grave (fome) caíram de 6,9% em 2004 para 5,0% em 2009, no governo Lula. | Isso é o Brasil que dá certo. | 2004 e 2009 | [IBGE, PNAD 2004 e 2009, escala EBIA](https://sidra.ibge.gov.br/tabela/6665) |
| FOME-BR | brasil | 4,1% → 3,2% | No Brasil, os domicílios em insegurança alimentar grave (fome) caíram de 4,1% em 2023 para 3,2% em 2024, no governo Lula. | Isso é o Brasil que dá certo. | 2023 e 2024 | [IBGE, PNAD Contínua 2023 e 2024, escala EBIA](https://sidra.ibge.gov.br/tabela/6665) |
| SM-3T | brasil | Lula 1 e 2: +62,8% · Temer e Bolsonaro: +0,8% · Lula 3: +12,5% | Ganho real do salário mínimo (acima da inflação, IPCA) em cada governo. | Com Lula, continua e cresce. | dez/2002 a set/2026 | [Salário mínimo legal (Ipeadata) corrigido pelo IPCA (IBGE)](https://sidra.ibge.gov.br/tabela/1737) |
| MCMV-ORIGEM | brasil | 2009 | O Minha Casa Minha Vida foi criado em 2009 e retomado em 2023, nos governos Lula. | Foi o Lula que fez. | 2009 e 2023 | [Planalto (Lei 11.977/2009 (MP 459/2009); Lei 14.620/2023)](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/lei/l11977.htm) |
| BF-HOJE | brasil | 19.295.378 | No Brasil, 19.295.378 famílias recebem o Bolsa Família. | Com Lula, continua e cresce. | set/2026 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |

**Bloqueados**

| Modelo | Nível | Motivo | Valores |
|---|---|---|---|
| FOME-3T | brasil | contraste não verdadeiro: Lula 1–2 (2009) 5,0% não é menor que Temer/Bolsonaro (2018) 4,6% | {"2009": 5.0, "2018": 4.6, "2024": 3.2} |
| FMI | brasil | fonte oficial não conferida neste ambiente (BCB/Fazenda) |  |
| MAPA-FOME | brasil | relatório SOFI/FAO não conferido neste ambiente |  |
| CAMPUS | brasil | data oficial dos campi (MEC/Plataforma Nilo Peçanha) não disponível |  |
| EMPREGO-3T | brasil | RAIS/CAGED (MTE) não responde a este ambiente |  |

## Bloqueios no país inteiro, por motivo

| Motivo | Quantidade |
|---|---:|
| número pequeno | 29.977 |
| piora ou avanço pequeno | 9.525 |
| contraste não verdadeiro | 5.570 |
| bairro sem correspondência segura entre 2000 e 2010 | 2.058 |
| piora ou queda pequena | 390 |
| fonte oficial não conferida neste ambiente (BCB/Fazenda) | 1 |
| relatório SOFI/FAO não conferido neste ambiente | 1 |
| data oficial dos campi (MEC/Plataforma Nilo Peçanha) não disponível | 1 |
| RAIS/CAGED (MTE) não responde a este ambiente | 1 |
