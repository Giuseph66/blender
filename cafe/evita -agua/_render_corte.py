import bpy, bmesh, math, os
from mathutils import Vector
OUT = os.path.dirname(os.path.abspath(bpy.data.filepath))
src = bpy.data.objects['Evita_Agua']
ob = src.copy(); ob.data = src.data.copy(); bpy.context.scene.collection.objects.link(ob)
src.hide_render = True

bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x = -60 if v.co.x < 0 else 60
    v.co.y = 0.0 if v.co.y < 0 else 60
    v.co.z = -20 if v.co.z < 0 else 20
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('_cut'); bm.to_mesh(me); bm.free()
cut = bpy.data.objects.new('_cut', me); bpy.context.scene.collection.objects.link(cut)
m = ob.modifiers.new('b', 'BOOLEAN'); m.operation='DIFFERENCE'; m.object=cut; m.solver='EXACT'
bpy.context.view_layer.objects.active = ob
bpy.ops.object.modifier_apply(modifier=m.name)
bpy.data.objects.remove(cut, do_unlink=True)

SC = bpy.context.scene
SC.render.engine='BLENDER_WORKBENCH'; SC.render.resolution_x=1200; SC.render.resolution_y=500
sh = SC.display.shading
sh.light='STUDIO'; sh.color_type='SINGLE'; sh.single_color=(0.18,0.18,0.20)
sh.show_cavity=True; sh.show_object_outline=True
cd = bpy.data.cameras.new('_C'); cam = bpy.data.objects.new('_C', cd)
SC.collection.objects.link(cam); cam.data.type='ORTHO'; SC.camera=cam
cam.data.ortho_scale=80; cam.location=(0,200,3); cam.rotation_euler=(math.pi/2,0,math.pi)
SC.render.filepath=os.path.join(OUT,'preview_corte.png')
bpy.ops.render.render(write_still=True)
result='ok'
