"""CP05 v2: um robo (UR10) faz a tupiagem e aplica cola + borracha nos dois lados da peca,
com troca de ferramenta e gabarito basculante; no fim o gabarito solta a peca numa esteira curta.

Sem injetora e sem cartesiano: o dummy 'Ponto_Entrega_Cartesiano' marca onde o cartesiano do
arquivo base deve soltar a peca no gabarito.

Uso (CoppeliaSim 4.10 aberto, simulacao parada):  .venv/Scripts/python montar_celula_v2.py
Gera: celula_cp05_v2.ttt (cena) e celula_cp05_v2.ttm (modelo para arrastar no arquivo base).
"""
import math
import os
import time
from cena_util import *  # noqa: F401,F403  (sim, client, cores e helpers de forma)

simIK = client.require('simIK')

# (rode com uma cena nova e vazia aberta no CoppeliaSim)

chao = sim.getObject('/Floor', {'noError': True})
if chao != -1:
    sim.removeModel(chao)

celula = sim.createDummy(0.05)
sim.setObjectAlias(celula, 'Celula_CP05')
sim.setModelProperty(celula, 0)

caixa('Piso_Fabrica', [9, 7, 0.02], [0.5, 0.0, -0.011], [0.7, 0.71, 0.69], None)

# ---------------------------------------------------------------- gabarito basculante (trunnion)
Z_EIXO = 1.0       # altura do eixo de giro = centro da peca
gab = grupo('Gabarito_Basculante', celula, [0, 0, Z_EIXO])
caixa('Gabarito_Base', [1.7, 0.6, 0.08], [0, 0, 0.04], CINZA_ESC, gab)
for sx, nm in [(-1, 'Gabarito_Coluna_Motor'), (1, 'Gabarito_Coluna_Mancal')]:
    caixa(nm, [0.14, 0.3, Z_EIXO - 0.04], [sx * 0.78, 0, (Z_EIXO + 0.08) / 2], AMARELO, gab)
caixa('Servomotor_Giro', [0.2, 0.2, 0.22], [-0.95, 0, Z_EIXO], AZUL, gab)
cilindro('Redutor_Giro', 0.07, 0.12, [-0.8, 0, Z_EIXO], CINZA, gab, [0, math.pi / 2, 0])
cilindro('Mancal_Giro', 0.06, 0.1, [0.78, 0, Z_EIXO], CINZA, gab, [0, math.pi / 2, 0])

# quadro que gira em torno do eixo x; a peca fica presa no meio dele (as duas faces livres)
quadro = dummy('Gabarito_Quadro', [0, 0, Z_EIXO], gab, 0.04)
for (dx, dy, tx, ty, nm) in [(0, -0.235, 1.3, 0.05, 'Quadro_Frente'), (0, 0.235, 1.3, 0.05, 'Quadro_Fundo'),
                             (-0.63, 0, 0.05, 0.52, 'Quadro_Lado_Motor'), (0.63, 0, 0.05, 0.52, 'Quadro_Lado_Mancal')]:
    caixa(nm, [tx, ty, 0.04], [dx, dy, Z_EIXO], [0.35, 0.37, 0.4], quadro)
for sx, nm in [(-1, 'Quadro_Eixo_Motor'), (1, 'Quadro_Eixo_Mancal')]:
    cilindro(nm, 0.03, 0.1, [sx * 0.7, 0, Z_EIXO], ALUMINIO, quadro, [0, math.pi / 2, 0])
# grampos pneumaticos (abrem/fecham) e suportes da peca
k = 0
for sx in (-1, 1):
    caixa('Apoio_Peca_%d' % k, [0.12, 0.05, 0.03], [sx * 0.52, 0, Z_EIXO], CINZA, quadro)
    k += 1
for i, (x, y) in enumerate([(-0.3, -0.21), (0.3, -0.21), (-0.3, 0.21), (0.3, 0.21)]):
    caixa('Grampo_%d' % i, [0.06, 0.04, 0.08], [x, y, Z_EIXO], [0.95, 0.5, 0.1], quadro)
sensor_indutivo('Sensor_Peca_Gabarito', [0.0, -0.33, Z_EIXO], [-math.pi / 2, 0, 0], gab, 0.25)

# peca: painel com rebarba nas duas faces
painel = caixa('Painel', [0.9, 0.35, 0.06], [0, 0, Z_EIXO], GRAFITE, quadro)
caixa('Painel_Cobertura', [0.4, 0.12, 0.05], [-0.15, 0.08, Z_EIXO + 0.055], [0.2, 0.21, 0.24], painel)
caixa('Painel_Nervura_1', [0.7, 0.03, 0.025], [0.0, -0.06, Z_EIXO - 0.042], [0.2, 0.21, 0.24], painel)
caixa('Painel_Nervura_2', [0.7, 0.03, 0.025], [0.0, 0.06, Z_EIXO - 0.042], [0.2, 0.21, 0.24], painel)
CINZA_REB = [0.8, 0.8, 0.76]
for lado, zf in [('A', 0.027), ('B', -0.027)]:
    reb = dummy('Rebarba_' + lado, [0, 0, Z_EIXO + zf], painel, 0.005)
    caixa('Rebarba_%s_1' % lado, [0.96, 0.03, 0.006], [0.0, -0.19, Z_EIXO + zf], CINZA_REB, reb)
    caixa('Rebarba_%s_2' % lado, [0.03, 0.41, 0.006], [0.465, 0.0, Z_EIXO + zf], CINZA_REB, reb)
    caixa('Rebarba_%s_3' % lado, [0.96, 0.03, 0.006], [0.0, 0.19, Z_EIXO + zf], CINZA_REB, reb)
    caixa('Rebarba_%s_4' % lado, [0.03, 0.41, 0.006], [-0.465, 0.0, Z_EIXO + zf], CINZA_REB, reb)

# cordao de cola + perfil de borracha nas duas faces (pecas reveladas conforme o robo passa)
HX, HY = 0.43, 0.155
cantos = [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY), (-HX, -HY)]
lados = [(cantos[i], cantos[i + 1]) for i in range(4)]
for lado, sg in [('A', 1), ('B', -1)]:
    zt = Z_EIXO + sg * 0.03
    gc = dummy('Cordao_Cola_' + lado, [0, 0, zt], painel, 0.005)
    gp = dummy('Perfil_Vedacao_' + lado, [0, 0, zt], painel, 0.005)
    idx = 0
    for (a_, b_), nl in zip(lados, (18, 6, 18, 6)):
        for kk in range(nl):
            t0, t1 = kk / nl, (kk + 1) / nl
            p0 = (a_[0] + (b_[0] - a_[0]) * t0, a_[1] + (b_[1] - a_[1]) * t0)
            p1 = (a_[0] + (b_[0] - a_[0]) * t1, a_[1] + (b_[1] - a_[1]) * t1)
            cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            horiz = abs(p1[0] - p0[0]) > abs(p1[1] - p0[1])
            comp = math.dist(p0, p1) + (0.016 if kk == nl - 1 else 0.002)
            if kk == nl - 1:
                L_ = math.dist(a_, b_)
                cx += (b_[0] - a_[0]) / L_ * 0.007
                cy += (b_[1] - a_[1]) / L_ * 0.007
            tc = [comp, 0.009, 0.004] if horiz else [0.009, comp, 0.004]
            tp = [comp, 0.016, 0.010] if horiz else [0.016, comp, 0.010]
            caixa('Cola_%s_%02d' % (lado, idx), tc, [cx, cy, zt + sg * 0.002], [0.97, 0.9, 0.45], gc)
            caixa('Perfil_%s_%02d' % (lado, idx), tp, [cx, cy, zt + sg * 0.005], [0.04, 0.04, 0.04], gp)
            idx += 1
    for g in (gc, gp):
        for o in sim.getObjectsInTree(g):
            sim.setObjectInt32Param(o, sim.objintparam_visibility_layer, 0)

entrega = dummy('Ponto_Entrega_Cartesiano', [0, 0, Z_EIXO + 0.6], celula, 0.08)

# ---------------------------------------------------------------- robo UR10 em pedestal
RX, RY = 0.0, -0.62
caixa('Pedestal_Robo', [0.45, 0.45, 0.6], [RX, RY, 0.3], CINZA_ESC, celula)
robo = modelo('robots/non-mobile/UR10.ttm', 'Robo', [RX, RY, 0.6], celula, [0, 0, math.pi / 2])
sem_scripts(robo)
for sh in sim.getObjectsInTree(robo, sim.sceneobject_shape):
    estatico(sh)
juntas = sim.getObjectsInTree(robo, sim.sceneobject_joint)
links = [h for h in sim.getObjectsInTree(robo, sim.sceneobject_shape) if sim.getObjectAlias(h) == 'link']
flange = links[-1]
for i, j in enumerate(juntas):
    sim.setObjectAlias(j, 'Robo_junta%d' % (i + 1))
for i, l in enumerate(links):
    sim.setObjectAlias(l, 'Robo_link%d' % (i + 1))
for l in [h for h in sim.getObjectsInTree(robo, sim.sceneobject_shape) if 'visible' in sim.getObjectAlias(h)]:
    sim.setObjectAlias(l, 'Robo_' + sim.getObjectAlias(l))
troc = caixa('Trocador_Robo', [0.07, 0.07, 0.03], [0, 0, 0], ALUMINIO, None)
sim.setObjectParent(troc, flange, False)
sim.setObjectPosition(troc, [0, 0, 0.015], flange)
sim.setObjectOrientation(troc, [0, 0, 0], flange)

TCP = 0.22
tip = sim.createDummy(0.015)
sim.setObjectParent(tip, flange, False)
sim.setObjectPosition(tip, [0, 0, TCP], flange)
sim.setObjectOrientation(tip, [0, 0, 0], flange)
sim.setObjectAlias(tip, 'Robo_tip')
alvo = dummy('Robo_alvo', [0, 0, 1.5], celula, 0.03)

env = simIK.createEnvironment()
grp = simIK.createGroup(env)
simIK.setGroupCalculation(env, grp, simIK.method_damped_least_squares, 0.1, 99)
simIK.addElementFromScene(env, grp, robo, tip, alvo, simIK.constraint_pose)
HOME_CFG = [-0.32, 0.14, 1.68, -3.39, -1.57, 1.78]


def ik_para(pos, tent=40):
    sim.setObjectPosition(alvo, list(pos), sim.handle_world)
    sim.setObjectOrientation(alvo, [math.pi, 0, 0], sim.handle_world)
    for _ in range(tent):
        simIK.handleGroup(env, grp, {'syncWorlds': True, 'allowError': True})
    return math.dist(sim.getObjectPosition(tip, sim.handle_world), pos)


def para_home():
    for j, q in zip(juntas, HOME_CFG):
        sim.setJointPosition(j, q)


# procura uma configuracao "cotovelo para cima" sobre a peca e usa como home
import random
random.seed(3)
cotovelo = sim.getObject('/Robo_junta3')
melhor = None
for tentativa in range(60):
    cfg = [random.uniform(-math.pi, math.pi) for _ in range(6)]
    for j, q in zip(juntas, cfg):
        sim.setJointPosition(j, q)
    e = ik_para([0.0, -0.2, 1.4], 80)
    if e < 1e-3:
        zc = sim.getObjectPosition(cotovelo, sim.handle_world)[2]
        if melhor is None or zc > melhor[0]:
            melhor = (zc, [sim.getJointPosition(j) for j in juntas])
HOME_CFG = melhor[1]
print('home cotovelo z=%.2f' % melhor[0], [round(q, 2) for q in HOME_CFG])
para_home()
ZT = Z_EIXO + 0.035
erros, zmin = [], 9
for (px, py) in [(-0.45, -0.175), (0.45, -0.175), (0.45, 0.175), (-0.45, 0.175), (-0.45, -0.175)]:
    erros.append(ik_para([px, py, ZT]))
    zmin = min(zmin, sim.getObjectPosition(cotovelo, sim.handle_world)[2])
print('erro IK cantos (m):', [round(e, 4) for e in erros], 'cotovelo z min=%.2f' % zmin)

# ---------------------------------------------------------------- ferramentas no suporte de troca
SLOT = {'Fresa': [-0.85, -0.75, 1.0], 'Cola': [0.85, -0.75, 1.0]}
sup = grupo('Suporte_Ferramentas', celula)
for nome, p in SLOT.items():
    caixa('Suporte_%s_Coluna' % nome, [0.06, 0.06, p[2] + 0.06], [p[0], p[1] - 0.12, (p[2] + 0.06) / 2], CINZA, sup)
    caixa('Suporte_%s_Garfo' % nome, [0.14, 0.2, 0.02], [p[0], p[1] - 0.04, p[2] + 0.07], AMARELO, sup)


def pedaco(nome, local, cor, ferr, raio=None, tam=None, ori=(0, 0, 0)):
    if raio is not None:
        h = sim.createPrimitiveShape(sim.primitiveshape_cylinder, [raio * 2, raio * 2, tam], 2)
    else:
        h = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(tam), 2)
    estatico(h)
    sim.setObjectParent(h, ferr, False)
    sim.setObjectPosition(h, list(local), ferr)
    sim.setObjectOrientation(h, list(ori), ferr)
    return novo(h, nome, None, cor)


for nome, p in SLOT.items():
    para_home()
    e = ik_para(p, 80)
    print('erro IK suporte', nome, round(e, 4))
    f = sim.createDummy(0.01)
    sim.setObjectAlias(f, 'Ferramenta_' + nome)
    sim.setObjectPose(f, sim.getObjectPose(flange, sim.handle_world), sim.handle_world)
    if nome == 'Fresa':
        pedaco('Fresa_Acoplamento', [0, 0, 0.045], ALUMINIO, f, raio=0.045, tam=0.03)
        pedaco('Fresa_Flutuador', [0, 0, 0.075], LARANJA, f, raio=0.05, tam=0.04)
        pedaco('Fresa_Spindle', [0, 0, 0.14], ALUMINIO, f, raio=0.04, tam=0.1)
        pedaco('Fresa_Broca', [0, 0, 0.205], [0.85, 0.7, 0.2], f, raio=0.008, tam=0.035)
        pedaco('Fresa_Mangueira_Ar', [0.045, 0, 0.12], AZUL, f, raio=0.008, tam=0.08)
    else:
        pedaco('Cola_Acoplamento', [0, 0, 0.045], ALUMINIO, f, raio=0.045, tam=0.03)
        pedaco('Cola_Cabecote', [0, 0, 0.11], [0.3, 0.3, 0.34], f, tam=[0.12, 0.09, 0.1])
        pedaco('Cola_Valvula', [0.03, 0, 0.18], AMARELO, f, raio=0.018, tam=0.05)
        pedaco('Cola_Bico', [0, 0, 0.207], [0.9, 0.9, 0.9], f, raio=0.006, tam=0.025)
        pedaco('Cola_Rolete', [-0.05, 0, 0.2], PRETO, f, raio=0.022, tam=0.02, ori=(math.pi / 2, 0, 0))
        pedaco('Cola_Faca', [-0.05, 0.035, 0.18], ALUMINIO, f, tam=[0.01, 0.01, 0.05])
        pedaco('Cola_Guia_Perfil', [-0.05, -0.045, 0.12], PRETO, f, raio=0.007, tam=0.12)
    dummy('Slot_' + nome, p, sup, 0.02)
    sim.setObjectParent(f, sup, True)

para_home()
sim.setObjectPose(alvo, sim.getObjectPose(tip, sim.handle_world), sim.handle_world)

# ---------------------------------------------------------------- esteira curta de saida
YE = 1.05
est = grupo('Esteira_Saida', celula, [1.0, YE, 0.4])
X0, X1 = -0.6, 2.6
caixa('Esteira_Correia', [X1 - X0, 0.56, 0.02], [(X0 + X1) / 2, YE, 0.79], VERDE_ESTEIRA, est)
for s_ in (1, -1):
    caixa('Esteira_Trilho', [X1 - X0, 0.05, 0.12], [(X0 + X1) / 2, YE + s_ * 0.31, 0.75], ALUMINIO, est)
for i, x in enumerate([X0 + 0.15, 1.0, X1 - 0.15]):
    for s_ in (1, -1):
        caixa('Esteira_Pe_%d' % (i * 2 + (s_ > 0)), [0.05, 0.05, 0.69], [x, YE + s_ * 0.31, 0.345], CINZA, est)
for xr in (X0, X1):
    cilindro('Esteira_Rolo', 0.04, 0.58, [xr, YE, 0.76], CINZA_ESC, est, [math.pi / 2, 0, 0])
caixa('Motor_Esteira', [0.25, 0.2, 0.2], [X1 - 0.2, YE + 0.45, 0.66], AZUL, est)
caixa('Sensor_Fim_Esteira_Corpo', [0.04, 0.04, 0.06], [X1 - 0.25, YE - 0.36, 0.86], [0.2, 0.3, 0.8], est)
caixa('Calha_Gabarito_Esteira', [1.0, 0.55, 0.02], [0.0, 0.6, 0.9], ALUMINIO, est, [-0.45, 0, 0])
cont = caixa('Contenedor_Pecas', [1.0, 0.8, 0.5], [3.3, YE, 0.25], AZUL, est)

# ---------------------------------------------------------------- grade de protecao
grd = grupo('Grade_Protecao', celula)
PANE2 = 'equipment/panes/pane (grid) 2.0 x 2.0.ttm'
PANE1 = 'equipment/panes/pane grid 1.0 x 2.0.ttm'
PANE05 = 'equipment/panes/pane grid 0.5 x 2.0.ttm'
VIDRO1 = 'equipment/panes/pane glass 1.0 x 2.0.ttm'


def pane(arq, nome, x, y, rot):
    h = modelo(arq, nome, [x, y, 1.0], grd, [0, 0, rot])
    sem_scripts(h)


XA, XB, YA, YB = -1.5, 1.5, -1.55, 1.45
pane(PANE2, 'Grade_F1', XA, YA, 0)          # frente: 2.0 + porta 1.0
pane(VIDRO1, 'Porta_Acesso', XA + 2.0, YA, 0)
pane(PANE2, 'Grade_T1', XA, YB, 0)          # fundo
pane(PANE1, 'Grade_T2', XA + 2.0, YB, 0)
pane(PANE2, 'Grade_E1', XA, YA, math.pi / 2)    # lado esquerdo: 2.0 + 1.0 (y -1.75..1.35 = 3.1)
pane(PANE1, 'Grade_E2', XA, YA + 2.0, math.pi / 2)
pane(PANE2, 'Grade_D1', XB, YA, math.pi / 2)    # lado direito: abertura de 1 m para a esteira (y 0.45..1.45)
caixa('Intertravamento_Porta', [0.06, 0.04, 0.12], [XA + 2.95, YA - 0.04, 1.1], AMARELO, grd)
for yy, lado in [(0.47, 'A'), (1.43, 'B')]:
    caixa('Cortina_Saida_' + lado, [0.04, 0.04, 1.7], [XB, yy, 0.85], AMARELO, grd)
    caixa('Cortina_Saida_%s_topo' % lado, [0.05, 0.05, 0.05], [XB, yy, 1.72], PRETO, grd)
modelo('components/sensors/SICK S300 Fast.ttm', 'Scanner_Area', [XA + 0.15, YA + 0.15, 0.15], grd, [0, 0, math.pi / 4])
for (x, y, z), nm in [((XA + 0.1, YA - 0.08, 1.1), 'Emergencia_1'), ((XB - 0.1, YA - 0.08, 1.1), 'Emergencia_2')]:
    b = caixa(nm, [0.09, 0.07, 0.09], [x, y, z], AMARELO, grd)
    cilindro(nm + '_Botao', 0.025, 0.03, [x, y - 0.045, z], VERMELHO, b, [math.pi / 2, 0, 0])
for (x0, y0, x1, y1) in [(XA - 0.1, YA - 0.1, XB + 0.1, YA - 0.1), (XA - 0.1, YB + 0.1, XB + 0.1, YB + 0.1),
                         (XA - 0.1, YA - 0.1, XA - 0.1, YB + 0.1), (XB + 0.1, YA - 0.1, XB + 0.1, YB + 0.1)]:
    caixa('Faixa', [max(abs(x1 - x0), 0.08), max(abs(y1 - y0), 0.08), 0.003], [(x0 + x1) / 2, (y0 + y1) / 2, 0.0015], AMARELO, grd)

# ---------------------------------------------------------------- utilidades fora da grade
uti = grupo('Utilidades', celula)
caixa('Base_Tambor_Cola', [0.8, 0.8, 0.1], [-0.9, -2.45, 0.05], CINZA_ESC, uti)
cilindro('Tambor_Cola', 0.29, 0.88, [-0.9, -2.45, 0.54], AZUL, uti)
cilindro('Bomba_Cola', 0.07, 0.55, [-0.9, -2.45, 1.25], ALUMINIO, uti)
caixa('Controlador_Dosagem', [0.3, 0.2, 0.4], [-0.35, -2.3, 1.0], CINZA_ESC, uti)
segmento('Mangueira_Cola_1', [-0.9, -2.45, 1.5], [-0.2, YA - 0.05, 2.25], 0.018, PRETO, uti)
segmento('Mangueira_Cola_2', [-0.2, YA - 0.05, 2.25], [-0.2, RY - 0.24, 2.25], 0.018, PRETO, uti)
segmento('Mangueira_Cola_3', [-0.2, RY - 0.24, 2.25], [-0.2, RY - 0.24, 0.6], 0.018, PRETO, uti)
caixa('Suporte_Rolos_Base', [1.4, 0.5, 0.06], [0.9, -2.45, 0.03], CINZA_ESC, uti)
caixa('Suporte_Rolos_Coluna', [0.08, 0.08, 1.0], [0.9, -2.45, 0.53], CINZA, uti)
for xr, nm in [(0.5, 'Rolo_Perfil_A'), (1.3, 'Rolo_Perfil_B')]:
    cilindro(nm, 0.34, 0.09, [xr, -2.45, 0.9], PRETO, uti, [math.pi / 2, 0, 0])
    cilindro(nm + '_Cubo', 0.06, 0.12, [xr, -2.45, 0.9], ALUMINIO, uti, [math.pi / 2, 0, 0])
    segmento(nm + '_Braco', [xr, -2.45, 0.9], [0.9, -2.45, 0.9], 0.02, CINZA, uti)
caixa('Emendadora_Perfil', [0.2, 0.15, 0.15], [0.9, -2.45, 1.15], LARANJA, uti)
caixa('Buffer_Dancarino', [0.1, 0.1, 0.4], [0.9, -2.2, 1.45], AMARELO, uti)
segmento('Perfil_Alimentacao_1', [0.9, -2.2, 1.65], [0.2, YA - 0.05, 2.25], 0.01, PRETO, uti)
segmento('Perfil_Alimentacao_2', [0.2, YA - 0.05, 2.25], [0.2, RY - 0.24, 2.25], 0.01, PRETO, uti)
segmento('Perfil_Alimentacao_3', [0.2, RY - 0.24, 2.25], [0.2, RY - 0.24, 0.6], 0.01, PRETO, uti)
caixa('Painel_Eletrico_CLP', [0.4, 0.8, 1.9], [-2.1, 0.4, 0.95], [0.75, 0.75, 0.72], uti)
caixa('IHM_Pedestal', [0.06, 0.06, 1.2], [2.0, -2.1, 0.6], CINZA, uti)
ihm = caixa('IHM', [0.4, 0.06, 0.3], [2.0, -2.1, 1.3], CINZA_ESC, uti, [-0.3, 0, 0])
caixa('IHM_Tela', [0.34, 0.005, 0.22], [2.0, -2.07, 1.31], [0.15, 0.45, 0.85], ihm, [-0.3, 0, 0])
caixa('Torre_Sinal_Haste', [0.03, 0.03, 0.4], [XB + 0.15, YA - 0.1, 2.0], CINZA, uti)
cilindro('Torre_Sinal_Vermelho', 0.04, 0.07, [XB + 0.15, YA - 0.1, 2.24], [0.18, 0.18, 0.18], uti)
cilindro('Torre_Sinal_Amarelo', 0.04, 0.07, [XB + 0.15, YA - 0.1, 2.31], [0.18, 0.18, 0.18], uti)
cilindro('Torre_Sinal_Verde', 0.04, 0.07, [XB + 0.15, YA - 0.1, 2.38], [0.1, 0.9, 0.2], uti)
op = modelo('people/Standing Bill.ttm', 'Operador_Celula', [2.0, -2.7, 0], uti, [0, 0, math.pi / 2])
sem_scripts(op)

# ---------------------------------------------------------------- controlador + salvar
with open(os.path.join(AQUI, 'controlador_v2.lua'), encoding='utf-8') as f:
    codigo = f.read()
scr = sim.createScript(sim.scripttype_simulation, codigo, 0, 'lua')
sim.setObjectAlias(scr, 'Controlador_Celula')
sim.setObjectParent(scr, celula, True)

sim.setBoolParam(sim.boolparam_realtime_simulation, True)


def olhar(h, pos, alvo_):
    d = [alvo_[i] - pos[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d))
    z = [v / n for v in d]
    x = [-z[1], z[0], 0.0]
    nx = math.hypot(x[0], x[1])
    x = [v / nx for v in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    sim.setObjectMatrix(h, [x[0], y[0], z[0], pos[0], x[1], y[1], z[1], pos[1], x[2], y[2], z[2], pos[2]], sim.handle_world)


cam = sim.getObject('/DefaultCamera', {'noError': True})
if cam != -1:
    olhar(cam, [3.6, -4.2, 3.3], [0.3, 0.0, 0.8])
sim.setObjectSelection([])
sim.saveModel(celula, os.path.join(AQUI, 'celula_cp05_v2.ttm').replace('\\', '/'))
sim.saveScene(os.path.join(AQUI, 'celula_cp05_v2.ttt').replace('\\', '/'))
print('OK celula_cp05_v2.ttt / .ttm')
