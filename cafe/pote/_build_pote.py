import bpy, bmesh, math

# ================= PARAMETROS (mm) =================
L        = 167.0   # comprimento total (base = topo)
W_BIG    = 155.0   # lateral estendida, no topo
W_SML    =  95.0   # lateral menor, no topo
W_BASE   =  93.0   # largura da base
H        = 156.0   # altura total externa
T        =   3.0   # parede / fundo
DROP_Z   =  81.0   # abaixo disso a parede e reta em W_BASE

X_FLAT   =  24.0   # cava: fim do trecho reto em Y = W_SML
ANG_CAVA =  45.0   # cava: angulo do trecho reto
R_CAVA   =  75.0   # cava: raio do arco
XC_CAVA  =  72.0
YC_CAVA  = 144.0   # fundo do arco = 69
X_ARM    = 110.0   # parede do braco (face externa)
R_ARM    =  22.0   # filete do canto interno do braco
R_CORN   =   8.0   # cantos verticais externos
R_SOFT   =   1.5

REB      =  10.0   # rebaixo do topo da parede da frente
REB_W    =  10.0
EAR_X    = 154.0   # orelha: daqui ate L a frente fica na altura cheia

SQ2 = math.sqrt(2.0)
XF  = X_ARM - R_ARM                                     # centro do filete (fixo)
YF  = YC_CAVA - math.sqrt((R_CAVA-R_ARM)**2 - (XF-XC_CAVA)**2)
DCF = math.hypot(XF-XC_CAVA, YF-YC_CAVA)                # = R_CAVA - R_ARM

def profile(d):
    """contorno superior deslocado d para dentro. devolve (g, x_wall, xs_chave)"""
    Ra, Rf = R_CAVA + d, R_ARM + d
    y_flat = W_SML - d
    c45    = (W_SML + X_FLAT) - d*SQ2            # reta: y = c45 - x
    x1     = c45 - y_flat
    # reta x arco
    A = 2.0
    B = -2.0*XC_CAVA - 2.0*(c45 - YC_CAVA)
    C = XC_CAVA**2 + (c45 - YC_CAVA)**2 - Ra*Ra
    x2 = (-B + math.sqrt(B*B - 4*A*C)) / (2*A)
    # arco x filete (tangencia interna)
    x3 = XC_CAVA + Ra*(XF - XC_CAVA)/DCF
    x_wall = XF + Rf
    def g(x):
        x = min(max(x, 0.0), L)
        if x <= x1:     return y_flat
        if x <= x2:     return c45 - x
        if x <= x3:     return YC_CAVA - math.sqrt(max(Ra*Ra - (x-XC_CAVA)**2, 0.0))
        if x <  x_wall: return YF - math.sqrt(max(Rf*Rf - (x-XF)**2, 0.0))
        return W_BIG - d
    keys = [x1, x2, x3, x_wall]
    return g, x_wall, keys

def samples(d, x0, x1e):
    g, x_wall, (a,b,c,_) = profile(d)
    xs = [x0, a]
    xs += [a + (b-a)*i/6.0 for i in range(1,7)]
    xs += [b + (c-b)*i/30.0 for i in range(1,31)]
    xs += [c + (x_wall-c)*i/20.0 for i in range(1,20)]
    xs += [x_wall-0.03, x_wall+0.03, x1e]
    yb_lim = W_BASE - d
    prev = None
    fine = []
    for q in [x0 + (x1e-x0)*i/400.0 for i in range(401)]:
        cur = g(q) > yb_lim
        if prev is not None and cur != prev:
            fine += [q-0.03, q+0.03]
        prev = cur
    xs += fine
    return g, sorted({round(min(max(x,x0),x1e),4) for x in xs})

SC = bpy.context.scene
SC.unit_settings.system='METRIC'; SC.unit_settings.scale_length=0.001
SC.unit_settings.length_unit='MILLIMETERS'
for n in ("Pote_Cafe","_outer","_inner","_big","_small","_clip","_ear"):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.get("Pote_Cafe")
if col is None:
    col = bpy.data.collections.new("Pote_Cafe"); SC.collection.children.link(col)

def mk(name, bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name, me); col.objects.link(ob); return ob

def loft(name, ring_fn, xs):
    bm=bmesh.new(); rings=[]
    for x in xs:
        rings.append([bm.verts.new((x, y, z)) for (y, z) in ring_fn(x)])
    n=len(rings[0])
    for a,b in zip(rings, rings[1:]):
        for i in range(n):
            j=(i+1)%n
            try: bm.faces.new((a[i],a[j],b[j],b[i]))
            except ValueError: pass
    bm.faces.new(rings[0]); bm.faces.new(list(reversed(rings[-1])))
    return mk(name, bm)

def box(name,x0,x1,y0,y1,z0,z1):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts:
        v.co.x=(x0+x1)/2+v.co.x*(x1-x0); v.co.y=(y0+y1)/2+v.co.y*(y1-y0); v.co.z=(z0+z1)/2+v.co.z*(z1-z0)
    return mk(name,bm)

def boolean(t,c,op='DIFFERENCE'):
    m=t.modifiers.new(name="b",type='BOOLEAN'); m.object=c; m.operation=op; m.solver='EXACT'
    bpy.context.view_layer.objects.active=t
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(c, do_unlink=True)

def cleanup(ob):
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.02)
    bmesh.ops.dissolve_degenerate(bm, dist=0.02, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data); bm.free()

def round_corners(ob, r_corn, r_soft, xlo, xhi):
    bm=bmesh.new(); bm.from_mesh(ob.data)
    ve=[e for e in bm.edges
        if len(e.link_faces)==2
        and abs(e.verts[0].co.z-e.verts[1].co.z) > 20.0
        and e.calc_face_angle(0.0) > math.radians(40.0)
        and ((e.verts[0].co.x+e.verts[1].co.x)/2.0 < xlo+10.0
             or (e.verts[0].co.x+e.verts[1].co.x)/2.0 > xhi-10.0)]
    if ve: bmesh.ops.bevel(bm, geom=ve, offset=r_corn, segments=6,
                           affect='EDGES', profile=0.5, clamp_overlap=True)
    bm.to_mesh(ob.data); bm.free()
    m=ob.modifiers.new(name="soft",type='BEVEL')
    m.width=r_soft; m.segments=2; m.limit_method='ANGLE'
    m.angle_limit=math.radians(28); m.use_clamp_overlap=True
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    cleanup(ob)
    return len(ve)

bpy.ops.object.select_all(action='DESELECT')

# ---------- 1. externo: superficie regrada (W_BASE @ Z81  ->  perfil @ Z156) ----------
g_out, XS_OUT = samples(0.0, 0.0, L)
def ring_out(x):
    yb = min(g_out(x), W_BASE)      # a cava atravessa toda a altura
    return [(0.0,0.0), (yb,0.0), (yb,DROP_Z), (g_out(x),H), (0.0,H)]
outer = loft("_outer", ring_out, XS_OUT)
n_c = round_corners(outer, R_CORN, R_SOFT, 0.0, L)

# ---------- 2. cavidade ----------
ZTOP = 240.0
g_in, XS_IN = samples(T, T, L-T)
def ring_in(x):
    yt = g_in(x)
    yb = min(yt, W_BASE - T)
    y_far = yb + (ZTOP-DROP_Z)/(H-DROP_Z) * (yt - yb)
    return [(T,T), (yb,T), (yb,DROP_Z), (y_far,ZTOP), (T,ZTOP)]
inner = loft("_inner", ring_in, XS_IN)
round_corners(inner, R_CORN-T, R_SOFT*0.6, T, L-T)

body = outer; body.name = "Pote_Cafe"
boolean(body, inner)

# ---------- 3. rebaixo de 10 mm no topo da parede da frente ----------
def ruled_solid(name, d, yback, zbot, ztop, xs, g):
    def ring(x):
        yb = min(g(x), W_BASE - d)
        y_far = yb + (ztop-DROP_Z)/(H-DROP_Z)*(g(x) - yb)
        return [(yback,zbot), (yb,zbot), (yb,DROP_Z), (y_far,ztop), (yback,ztop)]
    return loft(name, ring, xs)

g_b, XS_B = samples(-3.0, 0.0, L)
g_s, XS_S = samples(REB_W, 0.0, L)
big   = ruled_solid("_big",   -3.0,  -3.0,   0.0, H+40.0, [-6.0]+XS_B+[L+6.0], g_b)
boolean(big, box("_clip", -60, L+60, -60, W_BIG+60, H-REB, H+100), op='INTERSECT')
small = ruled_solid("_small", REB_W, -10.0, -60.0, H+60.0, [-6.0]+XS_S+[L+6.0], g_s)
boolean(big, small)
boolean(big, box("_ear", EAR_X, L+60, -60, W_BIG+60, -60, H+100))
boolean(body, big)
cleanup(body)

bm=bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[e for e in bm.edges if len(e.link_faces)==0], context='EDGES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(body.data); bm.free()

for p in body.data.polygons: p.use_smooth=False
cube=bpy.data.objects.get("Cube")
if cube: cube.hide_viewport=True; cube.hide_render=True

bm=bmesh.new(); bm.from_mesh(body.data)
nm=len([e for e in bm.edges if len(e.link_faces)!=2]); vol=bm.calc_volume(signed=True); bm.free()
vs=[v.co for v in body.data.vertices]
_, xw_o, _ = profile(0.0); _, xw_i, _ = profile(T)
result={
 "dim":[round(v,2) for v in body.dimensions], "faces":len(body.data.polygons),
 "nao_manifold":nm, "volume_material_cm3":round(vol/1000.0,1), "cantos_bevel":n_c,
 "parede_braco_ext_X":round(xw_o,1), "parede_braco_int_X":round(xw_i,1),
 "cava_fundo_topo":round(min(g_out(x) for x in XS_OUT),1),
 "z_frente_meio": round(max((v.z for v in vs if 60<v.x<100 and v.y>60), default=-1),1),
 "z_orelha":      round(max((v.z for v in vs if v.x>158 and v.y>120), default=-1),1),
 "z_fundo_reto":  round(max((v.z for v in vs if v.x<10 and v.y<10), default=-1),1),
 "base_Y_max": round(max((v.y for v in vs if v.z<0.5), default=-1),1),
 "base_Y_min_cava": round(min((v.y for v in vs if v.z<0.5 and 60<v.x<90), default=-1),1),
}
