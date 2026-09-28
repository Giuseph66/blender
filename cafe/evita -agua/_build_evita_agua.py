import bpy, bmesh, math, os, mathutils

# ================= PARAMETROS (mm) =================
H         =  6.0   # altura total
T_BASE    =  2.0   # altura da base (o resto = paredes)

D_BASE    = 72.0   # diametro externo da base
D_W_OUT   = 67.0   # perimetro maior: face EXTERNA da parede
D_W_IN    = 50.0   # perimetro menor: face INTERNA (= furo)
T_WALL    =  1.5   # espessura das duas paredes
# entre as duas paredes: vazio, so base
# dentro do furo D_W_IN: sem base (passante)

R_BORE    =  1.5   # raio na quina interna da base (furo x face inferior)
R_ROOT    =  1.2   # raio no pe das paredes, dentro do vao
ROOT_ON   = True

# --- janela passante (recorte junto ao furo) ---
WIN_CHORD =  20.0  # largura da janela (corda)
WIN_GAP   =  0.3   # recuo ate o pe da parede maior (evita tangencia exata)

# --- sulco guia da bruma: vala em U na parede maior ---
SULCO_W    =  2.0  # largura da vala (= 2x raio do fundo)
SULCO_SIDE = +1.0  # +1 = borda esquerda da janela, -1 = borda direita
SULCO_Y    = SULCO_SIDE * (WIN_CHORD / 2.0 - SULCO_W / 2.0)

R_SOFT    =  0.4 
SEGS      = 256
ARC_SEGS  = 16

OUT_DIR = os.path.dirname(os.path.abspath(bpy.data.filepath or __file__))
NAME    = 'Evita_Agua'

R_HOLE  = D_W_IN / 2.0                    # 25.0  furo
R_WI_O  = R_HOLE + T_WALL                 # 26.5  parede menor, face externa
R_WO_O  = D_W_OUT / 2.0                   # 33.5  parede maior, face externa
R_WO_I  = R_WO_O - T_WALL                 # 32.0  parede maior, face interna
R_BASE  = D_BASE / 2.0                    # 36.0  borda da base
R_WIN   = R_WO_I - WIN_GAP

# ================= CENA LIMPA =================
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for me in list(bpy.data.meshes):
    bpy.data.meshes.remove(me)

SC = bpy.context.scene
SC.unit_settings.system = 'METRIC'
SC.unit_settings.scale_length = 0.001
SC.unit_settings.length_unit = 'MILLIMETERS'


def new_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    SC.collection.objects.link(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)


def cyl(name, r, z0, z1, segs=SEGS):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r, radius2=r, depth=(z1 - z0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, (z0 + z1) / 2.0))
    return new_obj(name, bm)


def cyl_x(name, r, x0, x1, y, z, segs=48):
    """cilindro deitado no eixo X"""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r, radius2=r, depth=(x1 - x0))
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                     matrix=mathutils.Matrix.Rotation(math.pi / 2.0, 3, 'Y'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=((x0 + x1) / 2.0, y, z))
    return new_obj(name, bm)


def boolean(target, cutter, op='DIFFERENCE'):
    m = target.modifiers.new('bool', 'BOOLEAN')
    m.operation = op
    m.object = cutter
    m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)



def arc(cr, cz, rad, a0, a1, n=ARC_SEGS, skip_first=True, skip_last=False):
    """pontos (r,z) de um arco, angulos em graus"""
    pts = []
    for i in range(n + 1):
        if skip_first and i == 0:
            continue
        if skip_last and i == n:
            continue
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cr + rad * math.cos(a), cz + rad * math.sin(a)))
    return pts


# ================= CORPO: revolucao do perfil em U =================
# perfil (r, z) anti-horario no plano XZ, de dentro para fora pelo fundo
prof = [(R_HOLE + R_BORE, 0.0)]                      # fim do raio do furo
prof += [(R_BASE, 0.0),
         (R_BASE, T_BASE),
         (R_WO_O, T_BASE),
         (R_WO_O, H),
         (R_WO_I, H)]

if ROOT_ON:                                           # pe da parede maior
    prof += [(R_WO_I, T_BASE + R_ROOT)]
    prof += arc(R_WO_I - R_ROOT, T_BASE + R_ROOT, R_ROOT, 0, -90)
    prof += [(R_WI_O + R_ROOT, T_BASE)]               # piso do vao
    prof += arc(R_WI_O + R_ROOT, T_BASE + R_ROOT, R_ROOT, -90, -180)
else:
    prof += [(R_WO_I, T_BASE), (R_WI_O, T_BASE)]

prof += [(R_WI_O, H), (R_HOLE, H)]                    # parede menor
prof += [(R_HOLE, R_BORE)]                            # desce pelo furo
prof += arc(R_HOLE + R_BORE, R_BORE, R_BORE, 180, 270, skip_last=True)  # quina da base

bm = bmesh.new()
vs = [bm.verts.new((r, 0.0, z)) for r, z in prof]
es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1),
               dvec=(0, 0, 0), angle=2 * math.pi, steps=SEGS, use_duplicate=False)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
body = new_obj(NAME, bm)

# ================= JANELA passante =================
win = box('_win', R_HOLE - 6.0, R_BASE + 6.0,
          -WIN_CHORD / 2.0, WIN_CHORD / 2.0, -2.0, H + 2.0)
boolean(win, cyl('_winlim', R_WIN, -3.0, H + 3.0), op='INTERSECT')
boolean(body, win)

# ================= SULCO em U (vala) na parede maior =================
rs = SULCO_W / 2.0
X0, X1 = R_HOLE - 6.0, R_BASE + 6.0
sul = box('_sulco', X0, X1, SULCO_Y - rs, SULCO_Y + rs, T_BASE + rs, H + 2.0)
boolean(sul, cyl_x('_sulcoR', rs, X0, X1, SULCO_Y, T_BASE + rs), op='UNION')
boolean(body, sul)

# ================= LIMPEZA antes do bevel =================
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(body.data)
bm.free()

# ================= ACABAMENTO =================
if R_SOFT > 0:
    m = body.modifiers.new('bev', 'BEVEL')
    m.width = R_SOFT
    m.segments = 3
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(35)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=m.name)

for p in body.data.polygons:
    p.use_smooth = False
body.data.update()

# ================= CHECAGEM =================
bm = bmesh.new()
bm.from_mesh(body.data)
nm = len([e for e in bm.edges if len(e.link_faces) != 2])
vol = abs(bm.calc_volume(signed=True))
bm.free()

stl = os.path.join(OUT_DIR, 'evita_agua.stl')
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True, global_scale=1.0)

blend = os.path.join(OUT_DIR, 'evita_agua.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend)

result = {
    'dim_mm': [round(v, 2) for v in body.dimensions],
    'faces': len(body.data.polygons),
    'nao_manifold': nm,
    'volume_cm3': round(vol / 1000.0, 2),
    'raios': dict(furo=R_HOLE, parede_menor_ext=R_WI_O, vao=[R_WI_O, R_WO_I],
                  parede_maior=[R_WO_I, R_WO_O], base=R_BASE),
    'stl': stl, 'blend': blend,
}
print('RESULT', result)
