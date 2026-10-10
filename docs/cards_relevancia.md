# Filtro de relevância dos cards

**Cards locais (bairro e cidade): 52.003 antes → 24.352 depois do filtro.** Estado e Brasil: 63 cards, que só entram quando o lugar tem menos de 3 cards locais. Teto: 5 por lugar e 2 por programa.

## Distribuição por tipo e programa

| Tipo | Programa | Antes | Depois |
|---|---|---:|---:|
| Antes e depois | Infraestrutura (Censo) | 5.859 | 1.465 |
| Antes e depois | Mortalidade infantil (Atlas) | 5.343 | 1.369 |
| Antes e depois | Pobreza (Atlas) | 5.416 | 3.612 |
| Está aqui | Bolsa Família | 10.435 | 4.378 |
| Está aqui | Cisternas | 1.297 | 795 |
| Está aqui | Mais Médicos | 3.179 | 2.788 |
| Está aqui | Pé-de-Meia | 4.931 | 2.779 |
| Está aqui | UBS | 7.068 | 0 |
| Origem (autoria) | Bolsa Família | 5.296 | 4.378 |
| Origem (autoria) | Mais Médicos | 3.179 | 2.788 |

## Cobertura

- Cidades com pelo menos 1 card local: 5.516 de 5.570; com menos de 3 (recebem estado/Brasil): 755.
- Bairros com card próprio: 1.341.

## Motivo dos cortes

| Motivo | Programa | Cards |
|---|---|---:|
| abaixo do limite de relevância | Bolsa Família | 2.638 |
| abaixo do limite de relevância | Cisternas | 389 |
| abaixo do limite de relevância | Infraestrutura (Censo) | 4.381 |
| abaixo do limite de relevância | Mais Médicos | 782 |
| abaixo do limite de relevância | Mortalidade infantil (Atlas) | 2.712 |
| abaixo do limite de relevância | Pobreza (Atlas) | 1.726 |
| abaixo do limite de relevância | Pé-de-Meia | 487 |
| abaixo do limite de relevância | UBS | 7.068 |
| fora dos melhores do lugar | Bolsa Família | 4.337 |
| fora dos melhores do lugar | Cisternas | 113 |
| fora dos melhores do lugar | Infraestrutura (Censo) | 13 |
| fora dos melhores do lugar | Mortalidade infantil (Atlas) | 1.262 |
| fora dos melhores do lugar | Pobreza (Atlas) | 78 |
| fora dos melhores do lugar | Pé-de-Meia | 1.665 |

## 10 cards cortados perto do limite

Margem = quanto o melhor critério do card atinge do limite (1,00 = no limite).

| Programa | Lugar | Card | Regra medida | Margem |
|---|---|---|---|---:|
| Bolsa Família | Balneário Barra do Sul (SC) | Balneário Barra do Sul (SC): 869 famílias recebem o Bolsa Família. | 14.99% das famílias (mín. 15%) e 2.540 pessoas (mín. 5.000) | 1.00 |
| Bolsa Família | Corumbataí (SP) | Corumbataí (SP): 186 famílias recebem o Bolsa Família. | 12.76% das famílias (mín. 15%) e 478 pessoas (mín. 5.000) | 0.85 |
| Mais Médicos | Mutuípe (BA) | Mutuípe (BA): 2 médicos do Mais Médicos atendem hoje. | 1.00 médicos por 10 mil hab. (mín. 1); 2 médicos, 20.037 hab. | 1.00 |
| Mais Médicos | Cupira (PE) | Cupira (PE): 2 médicos do Mais Médicos atendem hoje. | 0.85 médicos por 10 mil hab. (mín. 1); 2 médicos, 23.518 hab. | 0.85 |
| Cisternas | Guamaré (RN) | Guamaré (RN): 487 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | 9.92% dos domicílios (mín. 10%) e 487 cisternas (mín. 1.000) | 0.99 |
| Pé-de-Meia | Palma Sola (SC) | Palma Sola (SC): estudantes daqui receberam 76 parcelas do Pé-de-Meia em jun/2026. | 1.00% da população (mín. 1.0%) e 76 parcelas (mín. 1.000) | 1.00 |
| Infraestrutura (Censo) | Centro, Mossoró (RN) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Centro (Mossoró) passaram de 73% para 98%. | +24.97 p.p. (mín. +25 p.p. para infraestrutura) | 1.00 |
| Infraestrutura (Censo) | Enseada, São Sebastião (SP) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Enseada (São Sebastião) passaram de 1% para 23%. | +21.25 p.p. (mín. +25 p.p. para infraestrutura) | 0.85 |
| Pobreza (Atlas) | Olho d'Água do Borges (RN) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Olho d'Água do Borges caiu de 53,8% para 32,3%. | redução de 40.0% (mín. 40%), base 53,8 (mín. 5) | 1.00 |
| Mortalidade infantil (Atlas) | São Luiz do Anauá (RR) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em São Luiz do Anauá caiu de 31,6 para 19,0. | redução de 39.9% (mín. 40%), base 31,6 (mín. 20) | 1.00 |

## Carrossel final dos lugares de validação

**Várzea (Recife, PE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Recife (PE): 292 médicos do Mais Médicos atendem hoje. | 1.09 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| 2 | cidade | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 292 médicos do programa em Recife. | 1.09 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 3 | cidade | Recife (PE): 139.327 famílias recebem o Bolsa Família. | 0.72 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 4 | cidade | O Bolsa Família, que hoje atende 139.327 famílias em Recife, foi criado em 2003, no governo Lula. | 0.72 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 5 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Recife caiu de 25,7% para 13,2%. | 0.61 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Bom Jardim (Fortaleza, CE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | bairro | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Bom Jardim (Fortaleza) passaram de 10% para 41%. | 1.31 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |
| 2 | cidade | Fortaleza (CE): 303.317 famílias recebem o Bolsa Família. | 0.79 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 3 | cidade | O Bolsa Família, que hoje atende 303.317 famílias em Fortaleza, foi criado em 2003, no governo Lula. | 0.79 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 4 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Fortaleza caiu de 27,5% para 12,1%. | 0.71 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 5 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Fortaleza caiu de 34,6 para 15,8. | 0.56 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Guamá (Belém, PA)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | bairro | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Guamá (Belém) passaram de 11% para 38%. | 1.27 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |
| 2 | cidade | Belém (PA): 199 médicos do Mais Médicos atendem hoje. | 0.96 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| 3 | cidade | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 199 médicos do programa em Belém. | 0.96 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 4 | cidade | Belém (PA): 147.006 famílias recebem o Bolsa Família. | 0.76 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 5 | cidade | O Bolsa Família, que hoje atende 147.006 famílias em Belém, foi criado em 2003, no governo Lula. | 0.76 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |

**Exu (PE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Exu (PE): 7.939 famílias recebem o Bolsa Família. | 1.11 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 2 | cidade | O Bolsa Família, que hoje atende 7.939 famílias em Exu, foi criado em 2003, no governo Lula. | 1.11 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 3 | cidade | Exu (PE): 4 médicos do Mais Médicos atendem hoje. | 0.88 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| 4 | cidade | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 4 médicos do programa em Exu. | 0.88 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 5 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Exu caiu de 62,1 para 22,7. | 0.67 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Canudos (BA)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Canudos (BA): 6 médicos do Mais Médicos atendem hoje. | 1.50 | [Ministério da Saúde](https://apidadosabertos.saude.gov.br/v1/) |
| 2 | cidade | O Mais Médicos foi retomado em 2023, no governo Lula. Hoje são 6 médicos do programa em Canudos. | 1.50 | [Planalto (Lei 14.621/2023); Ministério da Saúde, 09/10/2026](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 3 | cidade | Canudos (BA): 3.901 famílias recebem o Bolsa Família. | 1.07 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 4 | cidade | O Bolsa Família, que hoje atende 3.901 famílias em Canudos, foi criado em 2003, no governo Lula. | 1.07 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 5 | cidade | Canudos (BA): 1.380 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | 0.75 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |

**Porto Alegre (RS)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Porto Alegre (RS): 80.592 famílias recebem o Bolsa Família. | 0.65 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 2 | cidade | O Bolsa Família, que hoje atende 80.592 famílias em Porto Alegre, foi criado em 2003, no governo Lula. | 0.65 | [Planalto (MP 132/2003, convertida na Lei 10.836/2004); MDS](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 3 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Porto Alegre caiu de 8,5% para 3,8%. | 0.60 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 4 | cidade | Porto Alegre (RS): estudantes daqui receberam 14.661 parcelas do Pé-de-Meia em jun/2026. | 0.51 | [CGU, Portal da Transparência](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) |

