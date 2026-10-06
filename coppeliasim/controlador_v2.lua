-- Controlador da celula CP05 v2 (CoppeliaSim 4.10)
-- Ciclo: cartesiano entrega no gabarito -> grampos fecham -> robo pega a fresa ->
--        tupiagem lado A -> gabarito gira 180 -> tupiagem lado B -> troca para o cabecote de cola ->
--        cola + borracha lado B -> gira -> cola + borracha lado A -> devolve ferramenta ->
--        gabarito bascula e solta a peca na esteira -> esteira leva ao contenedor

sim = require 'sim'
simIK = require 'simIK'
simUI = require 'simUI'

local Z_EIXO = 1.0
local Z_TOPO = Z_EIXO + 0.035        -- altura do TCP na borda da face de cima
local VEL_TUPIA = 0.28               -- m/s ao longo do contorno
local VEL_COLA = 0.25
local VEL_LIVRE = 0.9
local ATRASO_PERFIL = 0.06           -- o rolete vem 6 cm atras do bico

------------------------------------------------------------------- utilidades
local index = nil
local function obj(name, optional)
    if not index then
        index = {}
        for _, o in ipairs(sim.getObjectsInTree(sim.getObject(':'))) do
            local a = sim.getObjectAlias(o)
            if index[a] == nil then index[a] = o end
        end
    end
    local h = index[name] or -1
    if h == -1 and not optional then error('objeto nao encontrado: ' .. name) end
    return h
end
local function exists(h) return h and h ~= -1 end
local function setVisible(h, vis)
    for _, o in ipairs(sim.getObjectsInTree(h)) do
        sim.setObjectInt32Param(o, sim.objintparam_visibility_layer, vis and 1 or 0)
    end
end
local function color(h, rgb) sim.setShapeColor(h, nil, sim.colorcomponent_ambient_diffuse, rgb) end
local function lerp(a, b, t) return {a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t} end
local function dist(a, b) return math.sqrt((a[1] - b[1]) ^ 2 + (a[2] - b[2]) ^ 2 + (a[3] - b[3]) ^ 2) end
local function dist2(a, b) return math.sqrt((a[1] - b[1]) ^ 2 + (a[2] - b[2]) ^ 2) end
local function waitSec(t)
    local t0 = sim.getSimulationTime()
    while sim.getSimulationTime() - t0 < t do sim.step() end
end
local function moveTo(h, goal, speed, onStep)
    local start = sim.getObjectPosition(h, sim.handle_world)
    local d = dist(start, goal)
    if d < 1e-4 then return end
    local t0 = sim.getSimulationTime()
    while true do
        local t = math.min(1, (sim.getSimulationTime() - t0) * speed / d)
        sim.setObjectPosition(h, lerp(start, goal, t), sim.handle_world)
        if onStep then onStep(t) end
        if t >= 1 then break end
        sim.step()
    end
end

------------------------------------------------------------------- painel (UI) e log
local ui = nil
local st = {ok = 0, ciclo = 0, cola = 100, roloA = 100, roloB = 100, roloAtivo = 'A', ferramenta = 'nenhuma', lado = 'A'}
local function uiSet(id, txt) if ui then simUI.setLabelText(ui, id, txt) end end
local function log(txt)
    local antigo = sim.getStringProperty(sim.handle_scene, 'customData.debugLog', {noError = true}) or ''
    if #antigo > 6000 then antigo = antigo:sub(-3000) end
    sim.setStringProperty(sim.handle_scene, 'customData.debugLog', antigo .. string.format('%.2f %s\n', sim.getSimulationTime(), txt))
end
local function etapa(txt) uiSet(1, '<b>Etapa:</b> ' .. txt); log(txt) end
local function painel()
    uiSet(2, string.format('<b>Peças prontas:</b> %d    <b>Último ciclo:</b> %.1f s', st.ok, st.ciclo))
    uiSet(3, string.format('<b>Ferramenta no robô:</b> %s    <b>Face para cima:</b> %s', st.ferramenta, st.lado))
    uiSet(4, string.format('<b>Tambor de cola:</b> %d %%', math.floor(st.cola)))
    uiSet(5, string.format('<b>Rolo A:</b> %d %%   <b>Rolo B:</b> %d %%   (ativo: %s)', math.floor(st.roloA), math.floor(st.roloB), st.roloAtivo))
end

local lamp = {}
local function sinal(estado)
    local on = {verde = {0.1, 0.9, 0.2}, amarelo = {1, 0.8, 0.1}, vermelho = {1, 0.1, 0.1}}
    for nome, h in pairs(lamp) do if exists(h) then color(h, nome == estado and on[nome] or {0.18, 0.18, 0.18}) end end
end

------------------------------------------------------------------- robo
local R = {}
local function ikStep() simIK.handleGroup(R.env, R.group, {syncWorlds = true, allowError = true}) end
local function alvoNoTip()
    sim.setObjectPosition(R.target, sim.getObjectPosition(R.tip, sim.handle_world), sim.handle_world)
    sim.setObjectOrientation(R.target, {math.pi, 0, 0}, sim.handle_world)
end
local function robotMove(goal, speed, onStep)
    local start = sim.getObjectPosition(R.target, sim.handle_world)
    local d = dist(start, goal)
    local t0 = sim.getSimulationTime()
    while d > 1e-4 do
        local t = math.min(1, (sim.getSimulationTime() - t0) * speed / d)
        local p = lerp(start, goal, t)
        sim.setObjectPosition(R.target, p, sim.handle_world)
        ikStep()
        if onStep then onStep(p, t) end
        if t >= 1 then break end
        sim.step()
    end
end
local function robotHome()
    local cur = {}
    for i, j in ipairs(R.joints) do cur[i] = sim.getJointPosition(j) end
    local t0 = sim.getSimulationTime()
    while true do
        local t = math.min(1, (sim.getSimulationTime() - t0) / 1.2)
        for i, j in ipairs(R.joints) do sim.setJointPosition(j, cur[i] + (R.home[i] - cur[i]) * t) end
        if t >= 1 then break end
        sim.step()
    end
    alvoNoTip()
end
local function contorno(c, hx, hy, z)
    return {{c[1] - hx, c[2] - hy, z}, {c[1] + hx, c[2] - hy, z}, {c[1] + hx, c[2] + hy, z},
            {c[1] - hx, c[2] + hy, z}, {c[1] - hx, c[2] - hy, z}}
end
local function seguirContorno(pts, speed, onStep, onSegFim)
    local s = 0
    for i = 1, #pts - 1 do
        local a, b = pts[i], pts[i + 1]
        local L, base = dist(a, b), s
        robotMove(b, speed, function(p, t) if onStep then onStep(p, base + L * t) end end)
        s = s + L
        if onSegFim then onSegFim(i, lerp(a, b, 0.5)) end
    end
end

------------------------------------------------------------------- ferramentas
local function pegarFerramenta(nome)
    etapa('Troca de ferramenta: pegando ' .. (nome == 'Fresa' and 'a tupia (fresa)' or 'o cabeçote de cola + borracha'))
    local slot = sim.getObjectPosition(obj('Slot_' .. nome), sim.handle_world)
    robotMove({slot[1], slot[2], slot[3] + 0.25}, VEL_LIVRE)
    robotMove(slot, 0.3)
    waitSec(0.3)
    sim.setObjectParent(obj('Ferramenta_' .. nome), R.flange, true)
    st.ferramenta = nome == 'Fresa' and 'tupia (fresa flutuante)' or 'cabeçote cola + borracha'
    painel()
    robotMove({slot[1], slot[2], slot[3] + 0.25}, 0.3)
    robotHome()
end
local function devolverFerramenta(nome)
    etapa('Troca de ferramenta: devolvendo ' .. (nome == 'Fresa' and 'a tupia' or 'o cabeçote de cola'))
    local slot = sim.getObjectPosition(obj('Slot_' .. nome), sim.handle_world)
    robotMove({slot[1], slot[2], slot[3] + 0.25}, VEL_LIVRE)
    robotMove(slot, 0.3)
    waitSec(0.3)
    sim.setObjectParent(obj('Ferramenta_' .. nome), obj('Suporte_Ferramentas'), true)
    st.ferramenta = 'nenhuma'
    painel()
    robotMove({slot[1], slot[2], slot[3] + 0.25}, 0.3)
    robotHome()
end

------------------------------------------------------------------- gabarito
local H = {}
local function girarGabarito(ang, tempo)
    local a0 = sim.getObjectOrientation(H.quadro, sim.handle_world)[1]
    if H.anguloAtual then a0 = H.anguloAtual end
    local t0 = sim.getSimulationTime()
    while true do
        local t = math.min(1, (sim.getSimulationTime() - t0) / tempo)
        local s = t * t * (3 - 2 * t)
        local a = a0 + (ang - a0) * s
        sim.setObjectOrientation(H.quadro, {a, 0, 0}, sim.handle_world)
        H.anguloAtual = a
        if t >= 1 then break end
        sim.step()
    end
end
local function grampos(fechado)
    for i = 0, 3 do color(obj('Grampo_' .. i), fechado and {0.1, 0.75, 0.25} or {0.95, 0.5, 0.1}) end
    uiSet(6, '<b>Sensores:</b> peça no gabarito ' .. (fechado and '<font color="#1a9a3a">SIM</font>' or 'não') ..
        '   grampos ' .. (fechado and '<font color="#1a9a3a">fechados</font>' or 'abertos'))
end

------------------------------------------------------------------- peca
local function mostrarPecaBruta()
    setVisible(H.peca, true)
    for _, l in ipairs({'A', 'B'}) do
        setVisible(obj('Cordao_Cola_' .. l), false)
        setVisible(obj('Perfil_Vedacao_' .. l), false)
    end
end
local function prepararPeca()
    sim.setObjectOrientation(H.quadro, {0, 0, 0}, sim.handle_world)
    H.anguloAtual = 0
    sim.setObjectParent(H.peca, H.quadro, false)
    sim.setObjectPose(H.peca, H.pecaPose, sim.handle_world)
    mostrarPecaBruta()
    st.lado = 'A'
end
local function ladoParaCima() return (math.abs(H.anguloAtual) < 1) and 'A' or 'B' end

------------------------------------------------------------------- operacoes
local function tupiar()
    local lado = ladoParaCima()
    st.lado = lado; painel()
    etapa('Tupiagem: removendo a rebarba do lado ' .. lado)
    local c = sim.getObjectPosition(H.peca, sim.handle_world)
    local pts = contorno(c, 0.45, 0.175, Z_TOPO)
    local strips = {}
    for k = 1, 4 do strips[k] = obj(string.format('Rebarba_%s_%d', lado, k)) end
    local cavaco = sim.addDrawingObject(sim.drawing_points, 4, 0, -1, 3000, {0.85, 0.85, 0.85})
    robotHome()
    robotMove({pts[1][1], pts[1][2], Z_TOPO + 0.15}, VEL_LIVRE)
    robotMove(pts[1], 0.3)
    seguirContorno(pts, VEL_TUPIA, function(p)
        sim.addDrawingObjectItem(cavaco, {p[1] + (math.random() - 0.5) * 0.06, p[2] + (math.random() - 0.5) * 0.06, Z_EIXO - 0.05 - math.random() * 0.1})
    end, function(i, meio)
        -- esconde a tira de rebarba mais proxima do trecho que acabou de ser usinado
        local melhor, dmin = nil, 1e9
        for _, s in ipairs(strips) do
            local d = dist2(sim.getObjectPosition(s, sim.handle_world), meio)
            if d < dmin then melhor, dmin = s, d end
        end
        if melhor then setVisible(melhor, false) end
    end)
    robotMove({pts[1][1], pts[1][2], Z_TOPO + 0.15}, 0.4)
    sim.removeDrawingObject(cavaco)
end

local function colar()
    local lado = ladoParaCima()
    st.lado = lado; painel()
    etapa('Cola + borracha: bico aplica a cola e o rolete assenta o perfil (lado ' .. lado .. ')')
    local c = sim.getObjectPosition(H.peca, sim.handle_world)
    local pts = contorno(c, 0.43, 0.155, Z_TOPO)
    local cola, perfil = {}, {}
    for i = 0, 47 do
        local hc = obj(string.format('Cola_%s_%02d', lado, i))
        local hp = obj(string.format('Perfil_%s_%02d', lado, i))
        cola[#cola + 1] = {h = hc, p = sim.getObjectPosition(hc, sim.handle_world), on = false}
        perfil[#perfil + 1] = {h = hp, p = sim.getObjectPosition(hp, sim.handle_world), on = false}
    end
    setVisible(obj('Cordao_Cola_' .. lado), false)
    setVisible(obj('Perfil_Vedacao_' .. lado), false)
    sim.setObjectInt32Param(obj('Cordao_Cola_' .. lado), sim.objintparam_visibility_layer, 1)
    sim.setObjectInt32Param(obj('Perfil_Vedacao_' .. lado), sim.objintparam_visibility_layer, 1)
    local hist = {}
    robotHome()
    local function revelar(lista, ponto)
        for _, e in ipairs(lista) do
            if not e.on and dist2(e.p, ponto) < 0.03 then setVisible(e.h, true); e.on = true end
        end
    end
    robotMove({pts[1][1], pts[1][2], Z_TOPO + 0.15}, VEL_LIVRE)
    robotMove(pts[1], 0.3)
    seguirContorno(pts, VEL_COLA, function(p, s)
        revelar(cola, p)
        hist[#hist + 1] = {s = s, p = p}
        for i = #hist, 1, -1 do
            if hist[i].s <= s - ATRASO_PERFIL then revelar(perfil, hist[i].p); break end
        end
        st.cola = math.max(0, st.cola - 0.003)
        local k = st.roloAtivo == 'A' and 'roloA' or 'roloB'
        st[k] = st[k] - 0.025
        if st[k] <= 0 then
            st[k] = 100
            st.roloAtivo = st.roloAtivo == 'A' and 'B' or 'A'
            uiSet(7, 'Rolo de borracha acabou: <b>emenda automática</b> no outro rolo, sem parar')
        end
    end)
    for _, e in ipairs(cola) do setVisible(e.h, true) end
    for _, e in ipairs(perfil) do setVisible(e.h, true) end
    etapa('Faca pneumática corta o perfil (lado ' .. lado .. ')')
    waitSec(0.3)
    robotMove({pts[1][1], pts[1][2], Z_TOPO + 0.15}, 0.4)
    painel()
end

local function girarParaOutroLado()
    robotHome()
    local destino = ladoParaCima() == 'A' and math.pi or 0
    etapa('Gabarito gira 180° para expor o outro lado')
    sinal('amarelo')
    girarGabarito(destino, 2.0)
    sinal('verde')
    st.lado = ladoParaCima(); painel()
end

local function entregaCartesiano()
    etapa('Cartesiano (do arquivo base) entrega a peça no gabarito')
    local final = sim.getObjectPosition(H.peca, sim.handle_world)
    sim.setObjectParent(H.peca, -1, true)
    sim.setObjectPosition(H.peca, {final[1], final[2], final[3] + 0.6}, sim.handle_world)
    moveTo(H.peca, final, 0.5)
    sim.setObjectParent(H.peca, H.quadro, true)
    waitSec(0.3)
    grampos(true)
    etapa('Grampos pneumáticos fecham')
    waitSec(0.5)
end

local function descarregar()
    etapa('Gabarito bascula e solta a peça na esteira')
    grampos(false)
    girarGabarito(-0.75, 1.5)
    sim.setObjectParent(H.peca, -1, true)
    local p = sim.getObjectPosition(H.peca, sim.handle_world)
    local ye = sim.getObjectPosition(obj('Esteira_Correia'), sim.handle_world)
    local o0 = sim.getObjectOrientation(H.peca, sim.handle_world)
    local destino = {p[1], ye[2], 0.83}
    moveTo(H.peca, destino, 0.8, function(t)
        sim.setObjectOrientation(H.peca, {o0[1] * (1 - t), 0, 0}, sim.handle_world)
    end)
    sim.setObjectOrientation(H.peca, {0, 0, 0}, sim.handle_world)
    girarGabarito(0, 1.2)
    etapa('Esteira leva a peça pronta para o contenedor')
    moveTo(H.peca, {2.25, ye[2], 0.83}, 0.5)
    local cp = sim.getObjectPosition(obj('Contenedor_Pecas'), sim.handle_world)
    moveTo(H.peca, {cp[1], cp[2], 0.83}, 0.6)
    moveTo(H.peca, {cp[1], cp[2], cp[3] + 0.1}, 0.6)
    setVisible(H.peca, false)
    st.ok = st.ok + 1
end

------------------------------------------------------------------- callbacks
function sysCall_init()
    sim.setStringProperty(sim.handle_scene, 'customData.debugLog', '')
    H.quadro = obj('Gabarito_Quadro')
    H.peca = obj('Painel')
    H.pecaPose = sim.getObjectPose(H.peca, sim.handle_world)
    H.anguloAtual = 0
    lamp.verde = obj('Torre_Sinal_Verde', true)
    lamp.amarelo = obj('Torre_Sinal_Amarelo', true)
    lamp.vermelho = obj('Torre_Sinal_Vermelho', true)

    R.base = obj('Robo')
    R.joints = sim.getObjectsInTree(R.base, sim.sceneobject_joint)
    R.flange = obj('Robo_link' .. #R.joints)
    R.tip = obj('Robo_tip')
    R.target = obj('Robo_alvo')
    R.home = {}
    for i, j in ipairs(R.joints) do R.home[i] = sim.getJointPosition(j) end
    R.env = simIK.createEnvironment()
    R.group = simIK.createGroup(R.env)
    simIK.setGroupCalculation(R.env, R.group, simIK.method_damped_least_squares, 0.08, 60)
    simIK.addElementFromScene(R.env, R.group, R.base, R.tip, R.target, simIK.constraint_pose)
    alvoNoTip()
    H.ferrPose = {}
    for _, n in ipairs({'Fresa', 'Cola'}) do
        H.ferrPose[n] = sim.getObjectPose(obj('Ferramenta_' .. n), sim.handle_world)
    end

    ui = simUI.create([[<ui title="Célula CP05 - painel do CLP" closeable="false" resizable="false"
        placement="relative" position="12,12" layout="vbox">
        <label id="1" text="" style="font-size: 15px"/>
        <label id="2" text="" style="font-size: 14px"/>
        <label id="3" text="" style="font-size: 14px"/>
        <label id="4" text="" style="font-size: 14px"/>
        <label id="5" text="" style="font-size: 14px"/>
        <label id="6" text="" style="font-size: 14px"/>
        <label id="7" text="" style="font-size: 14px"/>
    </ui>]])
    painel()
    grampos(false)
    sinal('verde')
    local cort = sim.addDrawingObject(sim.drawing_lines, 2, 0, -1, 50, {1, 0.1, 0.1})
    local a = sim.getObjectPosition(obj('Cortina_Saida_A'), sim.handle_world)
    local b = sim.getObjectPosition(obj('Cortina_Saida_B'), sim.handle_world)
    for z = 0.25, 1.65, 0.1 do sim.addDrawingObjectItem(cort, {a[1], a[2], z, b[1], b[2], z}) end
end

function sysCall_thread()
    while true do
        local t0 = sim.getSimulationTime()
        prepararPeca()
        entregaCartesiano()
        pegarFerramenta('Fresa')
        tupiar()
        girarParaOutroLado()
        tupiar()
        devolverFerramenta('Fresa')
        pegarFerramenta('Cola')
        colar()
        girarParaOutroLado()
        colar()
        devolverFerramenta('Cola')
        robotHome()
        descarregar()
        st.ciclo = sim.getSimulationTime() - t0
        painel()
    end
end

function sysCall_cleanup()
    if ui then simUI.destroy(ui) end
    sim.setObjectOrientation(H.quadro, {0, 0, 0}, sim.handle_world)
    sim.setObjectParent(H.peca, H.quadro, false)
    sim.setObjectPose(H.peca, H.pecaPose, sim.handle_world)
    mostrarPecaBruta()
    for _, n in ipairs({'Fresa', 'Cola'}) do
        local f = obj('Ferramenta_' .. n)
        sim.setObjectParent(f, obj('Suporte_Ferramentas'), false)
        sim.setObjectPose(f, H.ferrPose[n], sim.handle_world)
    end
    for i, j in ipairs(R.joints) do sim.setJointPosition(j, R.home[i]) end
    grampos(false)
    sinal('verde')
end
