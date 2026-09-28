import bpy, math
from mathutils import Vector

body = bpy.data.objects['Pote_Cafe']
SC = bpy.context.scene
SC.render.engine = 'BLENDER_WORKBENCH'
SC.render.resolution_x = 900; SC.render.resolution_y = 900
SC.render.resolution_percentage = 100
SC.render.film_transparent = False
sh = SC.display.shading
sh.light = 'STUDIO'; sh.color_type = 'SINGLE'
sh.single_color = (0.45, 0.45, 0.48)
sh.show_cavity = True; sh.show_object_outline = True

cam = bpy.data.objects.get('_CamOrto')
if cam is None:
    cd = bpy.data.cameras.new('_CamOrto')
    cam = bpy.data.objects.new('_CamOrto', cd)
    SC.collection.objects.link(cam)
cam.data.type = 'ORTHO'
SC.camera = cam

bb = [body.matrix_world @ Vector(c) for c in body.bound_box]
ctr = sum(bb, Vector()) / 8.0
span = max(max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3))
cam.data.ortho_scale = span * 1.75
D = span * 4

views = {
    "sup":   (Vector((0, 0, 1)),            (0.0, 0.0, 0.0)),
    "frente":(Vector((0, -1, 0)),           (math.pi/2, 0.0, 0.0)),
    "lado":  (Vector((1, 0, 0)),            (math.pi/2, 0.0, math.pi/2)),
    "iso":   (Vector((0.9, -1.0, 0.8)).normalized(), (math.radians(58), 0.0, math.radians(42))),
}
out = {}
for name, (d, rot) in views.items():
    cam.location = ctr + d * D
    cam.rotation_euler = rot
    p = '/home/jesus/Neurelix/blender/cafe/preview_%s.png' % name
    SC.render.filepath = p
    bpy.ops.render.render(write_still=True)
    out[name] = p
result = out
