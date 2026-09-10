# AGENTS.md — Armação Jean Monnier F870

Modelo 3D paramétrico de uma armação de óculos real, reconstruída a partir de
23 fotos com paquímetro digital (`imagem_ref/`).

**Arquivo principal:** `oculos_jean_monnier_F870.blend`
**Collection:** `Oculos_JM_F870`

---

## Regra de ouro

A cena está em **milímetros**: `scene.unit_settings.scale_length = 0.001`,
`length_unit = 'MILLIMETERS'`. **1 unidade Blender = 1 mm.**

Nunca escale objetos para "consertar" tamanho — corrija a constante que gerou a
geometria e regenere. Todo objeto é construído por script via `bmesh`, não
modelado à mão.

---

## Identificação

Gravado na haste direita: `F870   55 □ 16   140`
Marca (haste esquerda): **Jean Monnier**

`55 □ 16 - 140` é o padrão da indústria: lente 55 mm, ponte 16 mm, haste 140 mm.

---

## Medidas (mm)

### Confirmadas — gravação na armação
| Símbolo | Medida | Valor |
|---|---|---|
| `A` | largura da lente | **55.0** |
| `DBL` | ponte | **16.0** |
| `TEMPLE_LEN` | comprimento da haste | **140.0** |

### Confirmadas — paquímetro digital
| Constante | Valor | Foto | O que é |
|---|---|---|---|
| — | 53.61 | `155948/51/53` | largura real da lente (nominal 55) |
| `DBL` | 16.82 | `160054` | ponte, ponto estreito |
| — | 18.24 | `160117` | vão entre aros na base do recorte nasal |
| altura ext. do aro | 35.16 | `160035` | **borda a borda, não a lente** |
| `RIM_DEPTH` | 6.30 | `160153` | profundidade do aro (frente→trás) |
| `LENS_THICK` | 3.44 | `160144` | espessura da lente na borda |
| `TH_F` | 7.31 | `160214` | altura da haste na dobradiça |
| `TH_B` | 4.26 | `160208` | altura da haste na ponta |
| `TEMPLE_THK` | 1.68 | `160202` | espessura lateral da haste |

### Derivadas — análise de pixels
| Constante | Valor | Método |
|---|---|---|
| `B` | **30.7** | perfil vertical de `160117`, escala 19.8 px/mm |
| `RIM_TOP` | 2.5 | idem |
| `RIM_BOT` | 2.0 | idem |
| `TOTAL_W` | 128.7 | varredura de silhueta em `155918` |
| `PANTO` | 3.2° | inclinação do trecho reto da haste, `155856` |
| `WRAP_DEG` | 7.0 | vista de topo `155847` |
| dobra da haste | início a 58% do comprimento, queda 21.8 mm | `155856` |

**Coerência que precisa se manter:** `B + RIM_TOP + RIM_BOT == 35.16`
(30.7 + 2.5 + 2.0 = 35.2 ✓). Se mexer em um, ajuste os outros.

### Medida não resolvida
**39.03 mm** (`160134/35`) — não foi identificada e **não é usada**. Não
assuma que é a altura do aro: essa é 35.16. Se descobrir, atualize aqui.

---

## Sistema de coordenadas

```
+X = direita do usuário       (o modelo é espelhado em X)
+Y = para a FRENTE do rosto   (hastes crescem em -Y)
+Z = para cima
origem = centro da ponte, na face frontal dos aros
```

O lado direito é construído com `sign = +1` e o esquerdo com `sign = -1`.
Toda função geradora aceita esse `sign` — não duplique código para os dois lados.

---

## Convenções de nomes

Prefixo `OC_` em tudo. Sufixo `_D` (direito) / `_E` (esquerdo).

```
OC_Aro_D/E          aro, seção retangular com sulco interno
OC_Lente_D/E        lente com bisel que encaixa no sulco
OC_Ponte            barra superior ligando os aros
OC_Plaqueta_D/E     plaquetas nasais
OC_Haste_D/E        haste
OC_Charneira_*      peças da dobradiça
OC_Pivo_D/E         Empty de rotação da haste
```

Um script que recria uma peça **deve remover a antiga primeiro** pelo nome,
senão o Blender cria `.001`, `.002` e a cena vira lixo:

```python
for n in ("OC_Aro_D", "OC_Aro_E"):
    if n in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
```

---

## Encaixe da lente

O aro tem um **sulco em V** na face interna (padrão da óptica) e a lente tem um
**bisel em V** correspondente. Não é interseção de sólidos — as superfícies
casam por construção, a partir das mesmas constantes:

| Constante | Valor | O que é |
|---|---|---|
| `GROOVE_DEPTH` | 0.60 | profundidade do sulco no aro |
| `GROOVE_WIDTH` | 0.80 | abertura do sulco |
| `BEVEL_ANGLE` | 100° | ângulo do V |
| `FIT_CLEARANCE` | 0.05 | folga por lado |

O contorno da lente e o contorno interno do aro vêm da **mesma função**
`rr()` (rounded rect). Se mudar os raios de canto de um, mude do outro —
senão a lente deixa de encaixar.

---

## Dobradiça

Charneira de **5 barris**: 3 no lado da frente, 2 no lado da haste, pino
passante. A haste é parentada a um Empty (`OC_Pivo_D/E`) posicionado no eixo do
pino, então a rotação em Z do Empty abre e fecha a haste.

```
0°   = haste fechada (paralela à frente)
95°  = haste aberta (posição de uso)
```

Limites de rotação são impostos por constraint no Empty — não force além.

---

## Como trabalhar nesta cena

**Não use `bpy.ops.render.render()`.** Ele congela a UI do Blender inteira
enquanto roda, e em sessão interativa isso parece um travamento. Para inspeção
visual use `get_screenshot_of_area_as_image(area_ui_type="VIEW_3D")`, que é
barato. Renderize só se o usuário pedir uma imagem final.

Outras armadilhas já encontradas:

- Blender 5.x: `mesh.use_auto_smooth` **não existe mais**. Use
  `polygon.use_smooth = True`.
- O nó Principled não se chama sempre `"Principled BSDF"` (muda com o idioma da
  UI). Busque por tipo: `next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')`.
- PIL **não** aplica orientação EXIF sozinho. As fotos de `imagem_ref/` têm
  orientation 1, 3 e 8 misturadas — sempre passe por
  `convert -auto-orient` ou `ImageOps.exif_transpose` antes de medir pixels.

---

## Calibração de fotos (se for remedir)

Não confie na régua gravada do paquímetro: ela fica num plano mais afastado que
o objeto e dá ~5% de erro. Calibre pelas **garras tocando a armação**, cuja
abertura é o valor no display:

```
foto 160117: garras = 361 px ↔ 18.24 mm  →  19.8 px/mm
```

Para curvas (a dobra da haste), calibre pelo **comprimento de arco** conhecido
(140 mm), nunca por extensão horizontal — a diferença deixou a ponta 2.35 mm
fora de lugar até ser corrigida.

---

## Estado atual

Validado: curva da haste bate com a foto com erro médio de **0.58 mm**
(máx 1.45 mm); arco = 140.01 mm.

Aberto:
- medida de 39.03 mm não identificada
- contorno do aro usa raios de canto escolhidos a olho, não medidos
- dobradiça é uma peça de boa qualidade genérica, **não** cópia da real
  (decisão do usuário)
