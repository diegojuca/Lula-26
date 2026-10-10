# Filtro de relevância dos cards

**Cards locais (bairro e cidade): 38.389 antes → 20.078 depois do filtro.** Estado e Brasil: 63 cards, que só entram quando o lugar tem menos de 3 cards locais. Teto: 5 por lugar e 1 por programa.

## Distribuição por tipo e programa

| Tipo | Programa | Antes | Depois |
|---|---|---:|---:|
| Antes e depois | Infraestrutura (Censo) | 5.859 | 1.341 |
| Antes e depois | Mortalidade infantil (Atlas) | 5.343 | 2.568 |
| Antes e depois | Pobreza (Atlas) | 5.416 | 3.690 |
| Está aqui | Bolsa Família | 5.296 | 4.378 |
| Está aqui | Cisternas | 1.297 | 908 |
| Está aqui | Mais Médicos | 3.179 | 2.788 |
| Está aqui | Pé-de-Meia | 4.931 | 4.405 |
| Está aqui | UBS | 7.068 | 0 |

## Cobertura

- Cidades com pelo menos 1 card local: 5.516 de 5.570; com menos de 3 (recebem estado/Brasil): 1.262.
- Bairros com card próprio: 1.341.

## Motivo dos cortes

| Motivo | Programa | Cards |
|---|---|---:|
| abaixo do limite de relevância | Bolsa Família | 918 |
| abaixo do limite de relevância | Cisternas | 389 |
| abaixo do limite de relevância | Infraestrutura (Censo) | 4.381 |
| abaixo do limite de relevância | Mais Médicos | 391 |
| abaixo do limite de relevância | Mortalidade infantil (Atlas) | 2.712 |
| abaixo do limite de relevância | Pobreza (Atlas) | 1.726 |
| abaixo do limite de relevância | Pé-de-Meia | 487 |
| abaixo do limite de relevância | UBS | 7.068 |
| fora dos melhores do lugar | Infraestrutura (Censo) | 137 |
| fora dos melhores do lugar | Mortalidade infantil (Atlas) | 63 |
| fora dos melhores do lugar | Pé-de-Meia | 39 |

## 10 cards cortados perto do limite

Margem = quanto o melhor critério do card atinge do limite (1,00 = no limite).

| Programa | Lugar | Card | Regra medida | Margem |
|---|---|---|---|---:|
| Bolsa Família | Balneário Barra do Sul (SC) | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 869 famílias em Balneário Barra do Sul. | 14.99% das famílias (mín. 15%) e 2.540 pessoas (mín. 5.000) | 1.00 |
| Bolsa Família | Corumbataí (SP) | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 186 famílias em Corumbataí. | 12.76% das famílias (mín. 15%) e 478 pessoas (mín. 5.000) | 0.85 |
| Mais Médicos | Mutuípe (BA) | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 2 médicos atendendo em Mutuípe. | 1.00 médicos por 10 mil hab. (mín. 1); 2 médicos, 20.037 hab. | 1.00 |
| Mais Médicos | Cupira (PE) | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 2 médicos atendendo em Cupira. | 0.85 médicos por 10 mil hab. (mín. 1); 2 médicos, 23.518 hab. | 0.85 |
| Cisternas | Guamaré (RN) | Em Guamaré, 487 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | 9.92% dos domicílios (mín. 10%) e 487 cisternas (mín. 1.000) | 0.99 |
| Pé-de-Meia | Palma Sola (SC) | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 9 mil a estudantes do ensino médio em Palma Sola em jun/2026. | 1.00% da população (mín. 1.0%) e 76 parcelas (mín. 1.000) | 1.00 |
| Infraestrutura (Censo) | Centro, Mossoró (RN) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Centro (Mossoró) passaram de 73% para 98%. | +24.97 p.p. (mín. +25 p.p. para infraestrutura) | 1.00 |
| Infraestrutura (Censo) | Enseada, São Sebastião (SP) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Enseada (São Sebastião) passaram de 1% para 23%. | +21.25 p.p. (mín. +25 p.p. para infraestrutura) | 0.85 |
| Pobreza (Atlas) | Olho d'Água do Borges (RN) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Olho d'Água do Borges caiu de 53,8% para 32,3%. | redução de 40.0% (mín. 40%), base 53,8 (mín. 5) | 1.00 |
| Mortalidade infantil (Atlas) | São Luiz do Anauá (RR) | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em São Luiz do Anauá caiu de 31,6 para 19,0. | redução de 39.9% (mín. 40%), base 31,6 (mín. 20) | 1.00 |

## Carrossel final dos lugares de validação

**Várzea (Recife, PE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 292 médicos atendendo no Recife. | 1.09 | [Ministério da Saúde; Planalto (Lei 14.621/2023)](https://apidadosabertos.saude.gov.br/v1/) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 2 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 139.327 famílias no Recife. | 0.72 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 3 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres no Recife caiu de 25,7% para 13,2%. | 0.61 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 4 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 7,4 milhões a estudantes do ensino médio no Recife em jun/2026. | 0.52 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |
| 5 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) no Recife caiu de 29,8 para 15,6. | 0.49 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Bom Jardim (Fortaleza, CE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | bairro | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Bom Jardim (Fortaleza) passaram de 10% para 41%. | 1.31 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |
| 2 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 303.317 famílias em Fortaleza. | 0.79 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 3 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Fortaleza caiu de 27,5% para 12,1%. | 0.71 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 4 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Fortaleza caiu de 34,6 para 15,8. | 0.56 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 5 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 14 milhões a estudantes do ensino médio em Fortaleza em jun/2026. | 0.53 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |

**Guamá (Belém, PA)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | bairro | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, os domicílios com esgoto por rede geral em Guamá (Belém) passaram de 11% para 38%. | 1.27 | [IBGE, Censos 2000 e 2010 (agregados por setor)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/) |
| 2 | cidade | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 199 médicos atendendo em Belém. | 0.96 | [Ministério da Saúde; Planalto (Lei 14.621/2023)](https://apidadosabertos.saude.gov.br/v1/) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 3 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 147.006 famílias em Belém. | 0.76 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 4 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Belém caiu de 24,4% para 13,0%. | 0.58 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 5 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 7,1 milhões a estudantes do ensino médio em Belém em jun/2026. | 0.53 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |

**Exu (PE)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 7.939 famílias em Exu. | 1.11 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 2 | cidade | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 4 médicos atendendo em Exu. | 0.88 | [Ministério da Saúde; Planalto (Lei 14.621/2023)](https://apidadosabertos.saude.gov.br/v1/) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 3 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Exu caiu de 62,1 para 22,7. | 0.67 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 4 | cidade | Em Exu, 1.393 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | 0.64 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 5 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 310 mil a estudantes do ensino médio em Exu em jun/2026. | 0.55 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |

**Canudos (BA)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Retomado em 2023, no governo Lula, o Mais Médicos tem hoje 6 médicos atendendo em Canudos. | 1.50 | [Ministério da Saúde; Planalto (Lei 14.621/2023)](https://apidadosabertos.saude.gov.br/v1/) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm) |
| 2 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 3.901 famílias em Canudos. | 1.07 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 3 | cidade | Em Canudos, 1.380 cisternas foram entregues pelo programa federal de cisternas até abr/2026. | 0.75 | [MDS, MI Social](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) |
| 4 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 127 mil a estudantes do ensino médio em Canudos em jun/2026. | 0.54 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |
| 5 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a mortalidade até 1 ano de idade (por mil nascidos vivos, estimativa) em Canudos caiu de 60,1 para 36,0. | 0.42 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |

**Porto Alegre (RS)**

| # | Nível | Card | Pontuação | Fonte |
|---|---|---|---:|---|
| 1 | cidade | Criado em 2003, no governo Lula, o Bolsa Família hoje atende 80.592 famílias em Porto Alegre. | 0.65 | [MDS, MI Social; Planalto (MP 132/2003, convertida na Lei 10.836/2004)](https://aplicacoes.mds.gov.br/sagi/vis/data3/data-explorer.php) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l10.836.htm) |
| 2 | cidade | Entre 2000 e 2010, década em que Lula governou de 2003 a 2010, a parcela de pessoas pobres em Porto Alegre caiu de 8,5% para 3,8%. | 0.60 | [Atlas do Desenvolvimento Humano (PNUD, Ipea, FJP), Censos 2000 e 2010](https://www.ipeadata.gov.br/) |
| 3 | cidade | Criado em 2024, no governo Lula, o Pé-de-Meia pagou R$ 3,1 milhões a estudantes do ensino médio em Porto Alegre em jun/2026. | 0.51 | [CGU, Portal da Transparência; Planalto (Lei 14.818/2024)](https://portaldatransparencia.gov.br/download-de-dados/pe-de-meia) · [norma](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14818.htm) |

