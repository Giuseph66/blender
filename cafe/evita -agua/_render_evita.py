import bpy, math, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(bpy.data.filepath))
body = bpy.data.objects['Evita_Agua']
SC = bpy.context.scene
SC.render.engine = 'BLENDER_WORKBENCH'
SC.render.resolution_x = 900; SC.render.resolution_y = 900
SC.render.resolution_percentage = 100
SC.render.film_transparent = False
sh = SC.display.shading
sh.light = 'STUDIO'; sh.color_type = 'SINGLE'
sh.single_color = (0.18, 0.18, 0.20)
sh.show_cavity = True; sh.show_object_outline = True

cd = bpy.data.cameras.new('_CamOrto')
cam = bpy.data.objects.new('_CamOrto', cd)
SC.collection.objects.link(cam)
cam.data.type = 'ORTHO'
SC.camera = cam

bb = [body.matrix_world @ Vector(c) for c in body.bound_box]
ctr = sum(bb, Vector()) / 8.0
span = max(max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3))
cam.data.ortho_scale = span * 1.3
D = span * 4

views = {
    "sup":  (Vector((0, 0, 1)), (0.0, 0.0, 0.0)),
    "lado": (Vector((0, -1, 0)), (math.pi/2, 0.0, 0.0)),
    "iso":  (Vector((0.9, -1.0, 0.8)).normalized(), (math.radians(58), 0.0, math.radians(42))),
}
for name, (d, rot) in views.items():
    cam.location = ctr + d * D
    cam.rotation_euler = rot
    SC.render.filepath = os.path.join(OUT, 'preview_%s.png' % name)
    bpy.ops.render.render(write_still=True)

# closeup do rasgo
tgt = Vector((30.0, 0.0, 3.0))
cam.data.ortho_scale = 22
d = Vector((0.85, -1.0, 0.75)).normalized()
cam.location = tgt + d * D
cam.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
SC.render.filepath = os.path.join(OUT, 'preview_rasgo.png')
bpy.ops.render.render(write_still=True)
result = 'ok'
