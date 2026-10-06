"""Funcoes de apoio para montar cenas no CoppeliaSim via ZMQ remote API."""
import math
import os
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

AQUI = os.path.dirname(os.path.abspath(__file__))
client = RemoteAPIClient()
sim = client.require('sim')
APP = sim.getStringParam(sim.stringparam_application_path)

# ---------------------------------------------------------------- cores
CINZA = [0.55, 0.57, 0.6]
CINZA_ESC = [0.22, 0.23, 0.26]
GRAFITE = [0.17, 0.18, 0.2]
ALUMINIO = [0.78, 0.8, 0.82]
VERDE_ESTEIRA = [0.16, 0.45, 0.3]
AMARELO = [0.98, 0.78, 0.1]
AZUL = [0.12, 0.35, 0.7]
AZUL_INJ = [0.15, 0.42, 0.55]
VERMELHO = [0.85, 0.12, 0.12]
LARANJA = [0.95, 0.5, 0.1]
PRETO = [0.06, 0.06, 0.06]


def novo(handle, nome, pai, cor=None):
    sim.setObjectAlias(handle, nome)
    if pai is not None:
        sim.setObjectParent(handle, pai, True)
    if cor is not None:
        sim.setShapeColor(handle, None, sim.colorcomponent_ambient_diffuse, cor)
    return handle


def estatico(h):
    sim.setObjectInt32Param(h, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(h, sim.shapeintparam_respondable, 0)


def caixa(nome, tam, pos, cor, pai, ori=(0, 0, 0)):
    h = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(tam), 2)
    estatico(h)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    sim.setObjectOrientation(h, list(ori), sim.handle_world)
    return novo(h, nome, pai, cor)


def cilindro(nome, raio, alt, pos, cor, pai, ori=(0, 0, 0)):
    h = sim.createPrimitiveShape(sim.primitiveshape_cylinder, [raio * 2, raio * 2, alt], 2)
    estatico(h)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    sim.setObjectOrientation(h, list(ori), sim.handle_world)
    return novo(h, nome, pai, cor)


def esfera(nome, raio, pos, cor, pai):
    h = sim.createPrimitiveShape(sim.primitiveshape_spheroid, [raio * 2] * 3, 0)
    estatico(h)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    return novo(h, nome, pai, cor)


def segmento(nome, p1, p2, raio, cor, pai):
    """Cilindro ligando p1 a p2 (mangueiras, perfil, cabos)."""
    d = [p2[i] - p1[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d))
    z = [v / L for v in d]
    ref = [0, 0, 1] if abs(z[2]) < 0.9 else [1, 0, 0]
    x = [ref[1] * z[2] - ref[2] * z[1], ref[2] * z[0] - ref[0] * z[2], ref[0] * z[1] - ref[1] * z[0]]
    n = math.sqrt(sum(v * v for v in x))
    x = [v / n for v in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    c = [(p1[i] + p2[i]) / 2 for i in range(3)]
    h = sim.createPrimitiveShape(sim.primitiveshape_cylinder, [raio * 2, raio * 2, L], 2)
    estatico(h)
    m = [x[0], y[0], z[0], c[0], x[1], y[1], z[1], c[1], x[2], y[2], z[2], c[2]]
    sim.setObjectMatrix(h, m, sim.handle_world)
    return novo(h, nome, pai, cor)


def dummy(nome, pos, pai, tam=0.02):
    h = sim.createDummy(tam)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    return novo(h, nome, pai)


def grupo(nome, pai, pos=(0, 0, 0)):
    h = sim.createDummy(0.001)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    sim.setObjectInt32Param(h, sim.objintparam_visibility_layer, 0)
    return novo(h, nome, pai)


def modelo(arquivo, nome, pos, pai, ori=(0, 0, 0)):
    h = sim.loadModel(os.path.join(APP, 'models', arquivo).replace('\\', '/'))
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    sim.setObjectOrientation(h, list(ori), sim.handle_world)
    return novo(h, nome, pai)


def sem_scripts(h):
    for s in sim.getObjectsInTree(h, sim.sceneobject_script):
        sim.removeObjects([s])


def sensor_indutivo(nome, pos, ori, pai, alcance=0.7):
    ip = [32, 32, 1, 1, 0, 0, 0, 0]
    fp = [0.0, alcance, 0.01, 0.01, 0.01, 0.01, 0.0, 0.01, 0.01, 0.0, 0.0, 0.0, 0.02, 0.0, 0.0]
    h = sim.createProximitySensor(sim.proximitysensor_ray, 16, 0, ip, fp)
    sim.setObjectPosition(h, list(pos), sim.handle_world)
    sim.setObjectOrientation(h, list(ori), sim.handle_world)
    novo(h, nome, pai)
    corpo = cilindro(nome + '_corpo', 0.012, 0.05, pos, [0.2, 0.3, 0.8], h, ori)
    return h


