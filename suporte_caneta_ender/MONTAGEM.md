# Suporte de caneta com mola — Ender 3

Substitui o hotend. A caneta entra por cima, reta, e fica sempre
pressionada para baixo por duas molas. Aceita caneta de Ø7 a Ø13 mm.

Três peças separadas, todas removíveis.

## Peças impressas

| Arquivo | O que é | Mesa | Altura | Orientação |
|---|---|---|---|---|
| `1_corpo_placa.stl` | placa de fixação + trilhos | 44 × 66 mm | 17 mm | costas planas na mesa |
| `2_tampa_molas.stl` | tampa que segura o topo das molas | 44 × 36 mm | 14 mm | face grande na mesa |
| `3_carro_caneta.stl` | carro que prende a caneta | 40 × 35 mm | 38 mm | em pé |

Todas já exportadas na orientação certa. **Nenhuma precisa de suporte** — os
balanços têm reforço a 45° e as cavas das molas abrem para a mesa.
Sugerido: 0.2 mm, 4 perímetros, 30% preenchimento.

## Ferragens

- 2 × M3 (fixação na Ender 3) — cabeça cilíndrica, comprimento conforme o carro
- 2 × M3 × 20 (prendem a tampa no corpo) — cabeça cilíndrica
- 2 × mola de compressão, Ø externo 4–6 mm, livre 20–24 mm
  (serve mola de caneta esferográfica)
- 1 × M4 × 25 (trava da caneta, auto-atarraxante no plástico)

## Montagem

1. Parafuse o **corpo** no carro X da Ender 3. Use o par de furos do meio
   (rebaixados 3.6 mm, a cabeça some abaixo da face de deslize) ou os rasgos
   de baixo, o que casar com a tua máquina.
2. Deslize o **carro** nos trilhos, de cima para baixo. Ele para nos batentes.
3. Ponha uma mola na cava de cada haste do carro, em volta do pino.
4. Encaixe a **tampa** no topo do corpo e prenda com os dois M3 × 20.
   As pontas de cima das molas entram nos bolsos da tampa.
5. Enfie a caneta por cima, atravessando a tampa até o carro.
6. Aperte o M4 no ressalto da frente. A caneta encosta no canal em V
   do fundo e se centraliza sozinha, seja fina ou grossa.

Para trocar de caneta ou dar manutenção: tira os dois M3 da tampa e o carro
sai inteiro pelo topo, com as molas.

## Calibração

Com a mesa no Z=0, baixe o eixo Z até o carro subir uns 3–5 mm nos trilhos.
Essa pré-carga é o que mantém a pressão constante na folha. O curso útil
é de 16 mm, então variação de altura da mesa é absorvida sem levantar a caneta.

## Fixação na impressora

Um par de **rasgos laterais escareados** na altura do meio da placa (Z = 38 mm).
Cobrem espaçamento de furo de **11 a 32 mm** entre centros.

Use **parafuso M3 escareado (DIN 965)** — a cabeça cônica afunda rente à face,
que é onde o carro desliza. Parafuso de cabeça cilíndrica ali travaria o carro.

Para abrir espaço, os trilhos são interrompidos num vão de 10 mm (Z 33–43).
O carro tem 30 mm de altura, então mantém no mínimo 20 mm de engate no trilho
em qualquer posição do curso — verificado em toda a faixa.

## Ajustes no .blend

`suporte_caneta_ender3.blend` guarda as três peças montadas, mais uma cópia
de referência da versão anterior (coleção `REFERENCIA`, deslocada para X = −90).

Variáveis principais: `BD` (furo da caneta), `VAP` (fundo do V),
`PX` (eixo das molas), `CL` (folga do trilho, 0.25 mm),
`SLOPE` (inclinação do rabo-de-andorinha, 0.6), `ZTOP` (plano de corte
entre corpo e tampa, Z = 66), `PY` (espessura da placa, 11 mm — todas as
cotas em Y derivam dela, então mudar só ela reposiciona tudo junto).
