# CP05 · Robotização do acabamento do painel automotivo

FIAP · CP05 (Montagem 3D de sistema robotizado), case Extension Dash.

**Apresentação:** https://gabrieldallape.github.io/cp05-robotica-celula/ (use as setas ‹ › ou as setas do teclado). Também em [PDF](CP05_Apresentacao.pdf).

## A proposta

Hoje, depois que o cartesiano tira o painel da injetora, três pessoas cortam a rebarba, passam a cola e colam a borracha de vedação. A proposta é uma célula com **um robô de 6 eixos** e um **gabarito basculante**:

1. O cartesiano (do arquivo base) entrega a peça no gabarito; grampos pneumáticos prendem.
2. O robô pega a **tupia** (fresa flutuante) e tira a rebarba do lado A.
3. O gabarito **gira 180°** e o robô tira a rebarba do lado B.
4. O robô troca para o **cabeçote de vedação** (bico de cola + rolete + faca) e aplica cola + borracha nos lados B e A.
5. O gabarito **bascula**, a peça desce pela calha e a **esteira** leva até o contenedor.

O ciclo simulado é de cerca de 80 s. O investimento estimado é de R$ 1,09 milhão, com payback de cerca de 2 anos (premissas no slide 11).

## Arquivos do CoppeliaSim (`coppeliasim/`)

| Arquivo | O que é |
|---|---|
| `celula_cp05_v2.ttt` | Cena pronta: abra no CoppeliaSim 4.10 e dê Play |
| `celula_cp05_v2.ttm` | A célula como modelo, para arrastar para dentro do arquivo base "Injetora com Robô cartesiano.ttt" |
| `controlador_v2.lua` | Script da animação (já embutido na cena e no modelo) |
| `montar_celula_v2.py`, `cena_util.py` | Reconstroem a cena pela ZMQ remote API |

**Para usar com o arquivo base:** abra o `.ttt` da injetora, carregue o `celula_cp05_v2.ttm` (File › Load model) e mova o modelo `Celula_CP05` até o dummy `Ponto_Entrega_Cartesiano` ficar onde o cartesiano solta a peça. Depois é só dar Play.

Feito no CoppeliaSim Edu 4.10. O robô é o UR10 da biblioteca do CoppeliaSim, animado por cinemática inversa (simIK).
