# CP05 · Peças da célula em OBJ (para importar no CoppeliaSim 4.0)

Todos os arquivos estão em **metros, com Z para cima**, e já na posição final da célula. Importe com a escala 1, sem centralizar: cada peça cai no lugar certo.

## Como importar no CoppeliaSim 4.0

1. File › Import › Mesh… e escolha o `.obj`. Dá para selecionar vários de uma vez.
2. Na janela de opções, deixe a **escala em 1** (metros) e marque a opção **Z para cima**, se aparecer. Se a peça vier deitada, importe de novo trocando essa opção.
3. Se a peça vier toda cinza (o 4.0 às vezes ignora o `.mtl`), dê duplo clique no ícone da peça na hierarquia › Adjust color. As cores sugeridas estão na tabela.

## Arquivos

| Arquivo | O que é | Cor sugerida |
|---|---|---|
| 01_gabarito_base | Base, colunas, servomotor e mancal do gabarito | amarelo / cinza escuro |
| 02_gabarito_quadro_giratorio | Quadro que gira 180° (eixo x, a 1,0 m de altura) + 4 grampos | cinza / laranja |
| 03_peca_painel | O painel automotivo (peça) | grafite |
| 04_peca_rebarba | Rebarba nas duas faces (some na tupiagem) | cinza claro |
| 05_peca_cordao_cola | Cordão de cola nas duas faces | amarelo claro |
| 06_peca_perfil_borracha | Borracha de vedação nas duas faces | preto |
| 07_pedestal_robo | Pedestal do robô (0,60 m de altura) | cinza escuro |
| 08_ferramenta_tupia | Tupia (fresa flutuante), **origem no encaixe do robô** | alumínio / laranja |
| 09_ferramenta_cola_borracha | Cabeçote: bico de cola, rolete e faca, **origem no encaixe** | cinza / amarelo / preto |
| 10_suporte_ferramentas | Suporte de troca com duas posições | cinza / amarelo |
| 11_esteira_saida | Esteira de saída, calha e motor | verde / alumínio |
| 12_contenedor_pecas | Contenedor das peças prontas | azul |
| 13_cortina_luz_e_intertravamento | Postes da cortina de luz + intertravamento da porta | amarelo |
| 14_botoes_emergencia | Botões de emergência | amarelo / vermelho |
| 15_faixas_piso | Faixa amarela no piso em volta da grade | amarelo |
| 16_tambor_cola_bomba_mangueira | Tambor, bomba, controlador e mangueira aérea | azul / preto |
| 17_rolos_borracha_emenda | Rolo duplo de borracha, emendadora e buffer | preto / laranja |
| 18_painel_eletrico_ihm | Painel elétrico (CLP) e IHM | cinza |
| 19_torre_sinalizacao | Torre de sinalização | verde / amarelo / vermelho |
| 20_trocador_ferramenta_punho | Trocador de ferramenta do punho, **origem no flange** | alumínio |

## O que vem da biblioteca do próprio CoppeliaSim (Model browser)

| Modelo | Posição (x, y, z) | Rotação em Z |
|---|---|---|
| robots/non-mobile/UR10 | 0,00 · −0,62 · 0,60 (em cima do pedestal) | 90° |
| equipment/panes/pane (grid) 2.0 x 2.0 | −1,50 · −1,55 · 1,00 (frente) | 0° |
| equipment/panes/pane glass 1.0 x 2.0 (porta) | 0,50 · −1,55 · 1,00 | 0° |
| equipment/panes/pane (grid) 2.0 x 2.0 | −1,50 · 1,45 · 1,00 (fundo) | 0° |
| equipment/panes/pane grid 1.0 x 2.0 | 0,50 · 1,45 · 1,00 (fundo) | 0° |
| equipment/panes/pane (grid) 2.0 x 2.0 | −1,50 · −1,55 · 1,00 (lado esquerdo) | 90° |
| equipment/panes/pane grid 1.0 x 2.0 | −1,50 · 0,45 · 1,00 (lado esquerdo) | 90° |
| equipment/panes/pane (grid) 2.0 x 2.0 | 1,50 · −1,55 · 1,00 (lado direito; a abertura de 0,45 a 1,45 é a saída da esteira) | 90° |
| components/sensors/SICK S300 Fast | −1,35 · −1,40 · 0,15 | 45° |
| people/Standing Bill | 2,00 · −2,70 · 0,00 (na IHM) | 90° |

Os painéis de grade ficam com a posição na ponta deles. Se algum aparecer deslocado, arraste até fechar o retângulo da faixa amarela.

## Montando o robô

1. Arraste o UR10 da biblioteca e coloque em 0 · −0,62 · 0,60, girado 90° em Z.
2. Importe o `08_ferramenta_tupia.obj` e o `20_trocador_ferramenta_punho.obj`. Eles vêm com a origem no ponto de encaixe.
3. Arraste cada um para dentro de **UR10_connection** (ou do último elo, UR10_link7), na hierarquia, e zere a posição e a rotação relativas.

A ferramenta de cola (`09`) fica no suporte, para mostrar a troca. Se quiser mostrar ela montada, faça o mesmo que no passo 3.

## Arquivo da injetora do portal

O arquivo base já tem a injetora e o cartesiano. Importe estas peças nele e mova tudo junto até o **centro do gabarito** (0 · 0 · 1,0 nestes arquivos) ficar embaixo do ponto onde o cartesiano solta a peça.
