import bpy, math
from mathutils import Vector, Euler

body = bpy.data.objects['Pote_Cafe']
SC = bpy.context.scene

PTS = [
  ("A1",  (  0.0,   0.0, 156.0)),
  ("A2",  (  0.0,  95.0, 156.0)),
  ("A3",  ( 74.0,  70.0, 156.0)),
  ("A4",  (110.0, 155.0, 156.0)),
  ("A5",  (167.0, 155.0, 156.0)),
  ("A6",  (167.0,   0.0, 156.0)),
  ("A7",  ( 92.0,   0.0,  81.0)),
  ("A8",  ( 92.0,   0.0,   0.0)),
  ("A9",  (  0.0,   0.0,   0.0)),
  ("A10", (  0.0,  93.0,   0.0)),
  ("A11", ( 74.0,  68.0,   0.0)),
  ("A12", ( 92.0,  71.0,   0.0)),
  ("A13", ( 40.0,  40.0,   3.0)),
]

VIEWS = {
  "sup":    ((0.0, 0.0, 1.0),            (0.0, 0.0, 0.0)),
  "frente": ((0.0, -1.0, 0.0),           (math.pi/2, 0.0, 0.0)),
  "lado":   ((1.0, 0.0, 0.0),            (math.pi/2, 0.0, math.pi/2)),
  "iso":    ((0.576, -0.640, 0.512),     (math.radians(59.2), 0.0, math.radians(42.0))),
}

col = bpy.data.collections.get("Cotas")
if col is None:
    col = bpy.data.collections.new("Cotas"); SC.collection.children.link(col)

def clear():
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

mat = bpy.data.materials.get("_cota")
if mat is None:
    mat = bpy.data.materials.new("_cota"); mat.diffuse_color = (1.0, 0.25, 0.05, 1.0)

CTR = Vector((83.5, 77.5, 78.0))

def build(view):
    d, rot = VIEWS[view]
    d = Vector(d).normalized()
    eul = Euler(rot, 'XYZ')
    right = Vector((1,0,0)); right.rotate(eul)
    up    = Vector((0,1,0)); up.rotate(eul)
    clear()
    for name, p in PTS:
        p = Vector(p)
        rel = p - CTR
        u = rel.dot(right); v = rel.dot(up)
        n = Vector((u, v)).normalized() if (u or v) else Vector((1,0))
        pos = p + right*(n.x*20.0) + up*(n.y*20.0) + d*40.0
        cu = bpy.data.curves.new(name, type='FONT')
        cu.body = name; cu.size = 11.0; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        ob = bpy.data.objects.new(name, cu)
        ob.rotation_euler = eul; ob.location = pos
        ob.data.materials.append(mat)
        col.objects.link(ob)
        # haste ligando o rotulo ao ponto
        me = bpy.data.meshes.new("l_"+name)
        me.from_pydata([p - pos*0 - pos + pos, pos], [(0,1)], [])
        me.vertices[0].co = p; me.vertices[1].co = pos
        lo = bpy.data.objects.new("l_"+name, me)
        col.objects.link(lo)

SC.render.engine = 'BLENDER_WORKBENCH'
SC.render.resolution_x = 1100; SC.render.resolution_y = 1100
sh = SC.display.shading
sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True; sh.show_object_outline=True
body.color = (0.62,0.63,0.66,1.0)

cam = bpy.data.objects.get('_CamOrto')
cam.data.type='ORTHO'; cam.data.ortho_scale = 300.0
SC.camera = cam

out={}
for view in VIEWS:
    build(view)
    d,rot = VIEWS[view]
    cam.location = CTR + Vector(d).normalized()*700.0
    cam.rotation_euler = rot
    p = '/home/jesus/Neurelix/blender/cafe/cotas_%s.png' % view
    SC.render.filepath = p
    bpy.ops.render.render(write_still=True)
    out[view]=p
result = out
