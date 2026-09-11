import bpy, math, os, json
from mathutils import Vector

ROOT = r'C:\Users\user\Desktop\3d test'
BLEND_PATH = os.path.join(ROOT, 'ARK_SHIP.blend')
SCENE_NAME = 'ARK SHIP | streamlined habitat vessel'

# ---------- scene / materials ----------
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for sc_old in list(bpy.data.scenes):
    if sc_old.name == SCENE_NAME:
        bpy.data.scenes.remove(sc_old)
sc = bpy.data.scenes.new(SCENE_NAME)
bpy.context.window.scene = sc
S = sc
sc.unit_settings.system = 'METRIC'
sc.unit_settings.length_unit = 'METERS'
sc.render.film_transparent = True

def mkmat(name, color, metallic=0.0, rough=.3):
    m = bpy.data.materials.new('ARK / ' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = rough
    return m

MAT = {
    'Hull': mkmat('Hull ceramic', (.52, .59, .64), .78, .24),
    'HullDark': mkmat('Hull shadow', (.075, .095, .11), .72, .28),
    'Frame': mkmat('Structural titanium', (.22, .29, .33), .88, .2),
    'Carbon': mkmat('Carbon truss', (.025, .035, .042), .36, .27),
    'Glass': mkmat('Untextured smoked glass', (.06, .14, .18), .52, .16),
    'Copper': mkmat('Thermal copper', (.54, .21, .07), .82, .23),
    'Ceramic': mkmat('Thermal ceramic', (.78, .80, .76), .25, .35),
    'Mark': mkmat('Hull marking', (.78, .23, .055), .45, .25),
    'Glow': mkmat('Cool white emissive', (.45, .75, 1.0), .15, .18),
}

STAGE_NAMES = [
    '01 Spine and pressure bulkheads', '02 Fusion drive and power bus',
    '03 Habitat pressure modules', '04 Curved ark shells',
    '05 Radiators and propulsion pods', '06 Command ring and docking',
    '07 Fairings, sensors and service details', '08 Final inspection and save'
]
COL = []
for label in STAGE_NAMES:
    c = bpy.data.collections.new(label)
    sc.collection.children.link(c)
    COL.append(c)
JOBS = [[] for _ in STAGE_NAMES]
CURRENT = 0
BUSY = False
ITER = None
PARTS = []
MESSAGE = 'Ready: build the central spine'
FRAME = 1

def add(stage, kind, name, p, dims, material='Hull', **kw):
    JOBS[stage].append(dict(kind=kind, name=name, p=tuple(p), dims=tuple(dims), material=material, **kw))
def box(st, name, p, dims, material='Hull', **kw): add(st, 'box', name, p, dims, material, **kw)
def cyl(st, name, p, radius, depth, material='Hull', axis='Z', **kw): add(st, 'cyl', name, p, (radius, depth), material, axis=axis, **kw)
def cone(st, name, p, r1, r2, depth, material='Hull', axis='Z', **kw): add(st, 'cone', name, p, (r1, r2, depth), material, axis=axis, **kw)
def torus(st, name, p, major, minor, material='Frame', axis='X', **kw): add(st, 'torus', name, p, (major, minor), material, axis=axis, **kw)
def sphere(st, name, p, radius, material='Hull', scale=(1, 1, 1), **kw): add(st, 'sphere', name, p, (radius,), material, scale=scale, **kw)
def rod(st, name, a, b, radius, material='Frame', **kw):
    a, b = Vector(a), Vector(b)
    add(st, 'rod', name, tuple((a + b) / 2), (radius, (b - a).length), material, direction=tuple(b - a), **kw)
def cable(st, name, points, radius=.018, material='Copper', **kw): add(st, 'cable', name, points[0], (radius,), material, points=points, **kw)
def label(st, text, p, size=.16, material='Ceramic', rot=(math.pi/2, 0, 0), **kw): add(st, 'label', text, p, (size,), material, rot=rot, **kw)

def panel(st, name, points, material='Hull', thickness=.06, **kw):
    add(st, 'panel', name, points[0], (thickness,), material, points=points, **kw)

def curved_shell(st, name, sign_z, sign_y, material='Hull', **kw):
    # Long tapered habitat wing: a swept ribbon in the X/Z plane.
    pts = []
    L = 5.15
    for i in range(25):
        u = -1.0 + 2.0 * i / 24.0
        x = L * u
        z = sign_z * (1.25 + 2.05 * math.cos(u * math.pi / 2.0))
        y = sign_y * 1.48
        width = .34 * (0.42 + .58 * (1 - abs(u)))
        pts.append((x, y - width, z))
        pts.append((x, y + width, z))
    add(st, 'panel', name, pts[0], (.085,), material, points=pts, shell=True, **kw)

# ---------- stage 01: spine and bulkheads ----------
box(0, 'Main pressure spine', (0, 0, 0), (10.8, .48, .48), 'Frame')
box(0, 'Spine upper keel', (0, 0, .33), (10.2, .18, .16), 'Carbon')
box(0, 'Spine lower keel', (0, 0, -.33), (10.2, .18, .16), 'Carbon')
for x in [-4.45, -2.9, -1.45, 0, 1.45, 2.9, 4.45]:
    torus(0, 'Spine bulkhead ring', (x, 0, 0), 1.05 if abs(x) < 4 else 1.22, .095, 'Frame')
    for a in range(0, 360, 45):
        r = math.radians(a)
        rod(0, 'Bulkhead spoke', (x, 0, 0), (x, 1.0 * math.cos(r), 1.0 * math.sin(r)), .026, 'Carbon')
for y in [-.82, .82]:
    box(0, 'Lateral cargo rail', (0, y, 0), (9.6, .08, .08), 'Frame')
for x in [-4.7, 4.7]:
    for y in [-.22, .22]:
        for z in [-.22, .22]: sphere(0, 'Structural fastener', (x, y, z), .055, 'Hull')
label(0, 'ARK / EXCELSIOR', (0, -.285, .28), .14, 'Ceramic')

# ---------- stage 02: reactor and power ----------
torus(1, 'Fusion containment ring', (-5.35, 0, 0), 1.38, .18, 'Copper')
cyl(1, 'Fusion chamber', (-5.35, 0, 0), 1.08, .9, 'HullDark', 'X')
cyl(1, 'Fusion inner core', (-5.83, 0, 0), .52, .10, 'Glow', 'X')
for i in range(12):
    a = i * math.tau / 12
    y, z = 1.13 * math.cos(a), 1.13 * math.sin(a)
    rod(1, 'Magnetic coil support', (-5.35, y*.76, z*.76), (-5.35, y, z), .045, 'Copper')
    cyl(1, 'Magnetic coil', (-5.35, y, z), .08, .22, 'Copper', 'X')
cone(1, 'Primary exhaust bell', (-6.25, 0, 0), 1.02, .48, 1.28, 'Ceramic', 'X')
cyl(1, 'Exhaust throat', (-6.9, 0, 0), .25, .28, 'Carbon', 'X')
for side in [-1, 1]:
    cable(1, 'Power bus cable', [(-4.9, side*.45, 0), (-3.8, side*.65, 0), (-2.2, side*.65, 0), (-1.0, side*.45, 0)], .035, 'Copper')
box(1, 'Power distribution box', (-2.25, 0, 0), (1.0, .75, .52), 'HullDark')
for x in [-2.55, -2.25, -1.95]: box(1, 'Power bus insulator', (x, -.44, 0), (.12, .10, .25), 'Ceramic')

# ---------- stage 03: habitat pressure modules ----------
for x in [-2.0, 0, 2.0]:
    cyl(2, 'Habitat pressure cylinder', (x, 0, 0), .86, 1.62, 'Hull', 'X')
    torus(2, 'Habitat end frame', (x-.77, 0, 0), .82, .065, 'Frame')
    torus(2, 'Habitat end frame', (x+.77, 0, 0), .82, .065, 'Frame')
    for a in range(0, 360, 45):
        r = math.radians(a)
        rod(2, 'Habitat longitudinal rib', (x-.78, .78*math.cos(r), .78*math.sin(r)), (x+.78, .78*math.cos(r), .78*math.sin(r)), .022, 'Carbon')
    for a in range(0, 360, 60):
        r = math.radians(a)
        box(2, 'Habitat observation blister', (x, 1.0*math.cos(r), 1.0*math.sin(r)), (.36, .14, .14), 'Glass')
for x in [-3.0, -1.0, 1.0, 3.0]:
    cyl(2, 'Spin bearing collar', (x, 0, 0), .98, .12, 'Frame', 'X')
label(2, 'HABITAT / 04', (0, -.90, .18), .12, 'HullDark')

# ---------- stage 04: the signature curved ark shells ----------
curved_shell(3, 'Upper port habitat shell', 1, -1, 'Hull')
curved_shell(3, 'Upper starboard habitat shell', 1, 1, 'Hull')
curved_shell(3, 'Lower port habitat shell', -1, -1, 'HullDark')
curved_shell(3, 'Lower starboard habitat shell', -1, 1, 'HullDark')
for z in [-1, 1]:
    for y in [-1, 1]:
        for x in [-4.4, 0, 4.4]:
            rod(3, 'Shell tension strut', (x, y*1.22, z*1.15), (x, y*1.48, z*1.7), .032, 'Carbon')
for x in [-3.7, 0, 3.7]:
    for y in [-1.48, 1.48]:
        torus(3, 'Shell service collar', (x, y, 0), .34, .045, 'Frame', 'X')

# ---------- stage 05: radiators, pods, heat management ----------
for side in [-1, 1]:
    for x in [-2.6, -.9, .9, 2.6]:
        box(4, 'Radiator spine', (x, side*1.32, 2.45), (1.35, .08, .07), 'Copper')
        for j in range(9):
            z = 1.78 + j*.17
            box(4, 'Radiator fin', (x, side*1.32, z), (.09, .48, .025), 'Ceramic')
    pod_y = side * 2.05
    for x in [-2.6, 0, 2.6]:
        cyl(4, 'Auxiliary maneuver pod', (x, pod_y, 0), .32, 1.08, 'HullDark', 'X')
        cone(4, 'Maneuver pod nose', (x+.62, pod_y, 0), .32, .10, .34, 'Hull', 'X')
        cyl(4, 'Maneuver nozzle', (x-.62, pod_y, 0), .13, .16, 'Glow', 'X')
        rod(4, 'Pod mount arm', (x, side*1.15, 0), (x, pod_y, 0), .04, 'Frame')
for x in [-3.4, -1.7, 0, 1.7, 3.4]:
    box(4, 'Thermal bus spine', (x, 0, -.68), (.05, .8, .08), 'Copper')

# ---------- stage 06: command ring, nose and docking ----------
torus(5, 'Forward command ring', (5.05, 0, 0), 1.62, .18, 'Frame')
torus(5, 'Forward ring pressure seal', (5.05, 0, 0), 1.22, .07, 'Hull')
cyl(5, 'Command core', (5.05, 0, 0), 1.05, .45, 'Glass', 'X')
for a in range(0, 360, 30):
    r = math.radians(a)
    rod(5, 'Command ring spoke', (5.05, 0, 0), (5.05, 1.55*math.cos(r), 1.55*math.sin(r)), .028, 'Carbon')
cone(5, 'Forward aerodynamic nose', (5.95, 0, 0), 1.0, .12, 1.55, 'Hull', 'X')
for side in [-1, 1]:
    box(5, 'Docking collar', (4.0, side*1.65, 0), (.54, .15, .42), 'Frame')
    torus(5, 'Docking collar ring', (4.3, side*1.78, 0), .34, .06, 'Frame', 'Y')
    rod(5, 'Docking boom', (4.0, side*1.18, 0), (4.3, side*1.78, 0), .045, 'Carbon')
for a in [-.55, 0, .55]:
    y = 1.55 * math.sin(a)
    z = 1.55 * math.cos(a)
    box(5, 'Command window frame', (5.26, y, z), (.18, .32, .16), 'HullDark')
    box(5, 'Command window blank lens', (5.36, y, z), (.035, .23, .10), 'Glass')
label(5, 'ARK / EXCELSIOR', (5.08, -.20, 1.50), .13, 'Ceramic', rot=(0, 0, 0))

# ---------- stage 07: service fairings and sensor details ----------
for x in [-4.2, -2.1, 0, 2.1, 4.2]:
    box(6, 'Top service fairing', (x, 0, 1.02), (.70, .44, .12), 'Hull')
    for y in [-.22, .22]:
        cyl(6, 'Fairing captive fastener', (x, y, 1.10), .035, .03, 'Frame')
for side in [-1, 1]:
    for x in [-4.3, -2.15, 0, 2.15, 4.3]:
        cable(6, 'External service cable', [(x-.35, side*1.2, .55), (x, side*1.35, .63), (x+.35, side*1.2, .55)], .015, 'Copper')
for x in [-4.8, 4.8]:
    torus(6, 'Lidar sensor guard', (x, 0, 0), .32, .045, 'Frame', 'X')
    sphere(6, 'Sensor dome', (x, 0, 0), .20, 'Glass', scale=(.55, 1, 1))
rod(6, 'Long range antenna mast', (2.8, 0, 1.0), (2.8, 0, 2.0), .025, 'Frame')
sphere(6, 'Antenna receiver', (2.8, 0, 2.08), .09, 'Glass')
for side in [-1, 1]:
    for x in [-1.2, 1.2]:
        box(6, 'Navigation beacon', (x, side*1.62, .16), (.20, .08, .08), 'Glow')
label(6, 'ORBITAL ARK / 01', (0, -.26, -.55), .11, 'Ceramic')

# ---------- constructors ----------
def make_panel_mesh(points, thickness):
    # Ribbon mesh with a solidify modifier, preserving the aerodynamic silhouette.
    verts = list(points)
    faces=[]
    for i in range(0, len(points)-2, 2): faces.append((i, i+1, i+3, i+2))
    mesh=bpy.data.meshes.new('Ark shell ribbon'); mesh.from_pydata(verts, [], faces); mesh.update()
    return mesh

def construct(job, stage):
    global FRAME, MESSAGE
    k=job['kind']; p=job['p']; d=job['dims']; o=None
    if k == 'box':
        bpy.ops.mesh.primitive_cube_add(size=1, location=p); o=bpy.context.object; o.dimensions=d; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    elif k == 'cyl':
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=d[0], depth=d[1], location=p); o=bpy.context.object
    elif k == 'cone':
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=d[0], radius2=d[1], depth=d[2], location=p); o=bpy.context.object
    elif k == 'torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=d[0], minor_radius=d[1], major_segments=64, minor_segments=16, location=p); o=bpy.context.object
    elif k == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=d[0], location=p); o=bpy.context.object; o.scale=job.get('scale',(1,1,1))
    elif k == 'rod':
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=d[0], depth=d[1], location=p); o=bpy.context.object
    elif k == 'panel':
        o=bpy.data.objects.new(job['name'], make_panel_mesh(job['points'], d[0])); sc.collection.objects.link(o)
        sol=o.modifiers.new('Aerodynamic shell thickness','SOLIDIFY'); sol.thickness=d[0]
        bev=o.modifiers.new('Manufactured edge radius','BEVEL'); bev.width=.035; bev.segments=3
    elif k == 'cable':
        cu=bpy.data.curves.new(job['name'],'CURVE'); cu.dimensions='3D'; cu.bevel_depth=d[0]; cu.bevel_resolution=4
        sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(job['points'])-1)
        for bp, q in zip(sp.bezier_points, job['points']): bp.co=q; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
        o=bpy.data.objects.new(job['name'],cu); sc.collection.objects.link(o)
    elif k == 'label':
        cu=bpy.data.curves.new(job['name'],'FONT'); cu.body=job['name']; cu.align_x='CENTER'; cu.size=d[0]; cu.extrude=.004
        o=bpy.data.objects.new(job['name'],cu); sc.collection.objects.link(o); o.location=p; o.rotation_euler=job.get('rot',(0,0,0))
    else:
        return
    o.name=job['name']; o.data.materials.append(MAT[job['material']]); o['assembly_stage']=stage+1; o['design_note']='Visual form concept; no manufacturing validation'
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[stage].objects.link(o)
    axis=job.get('axis','Z')
    if axis=='X': o.rotation_euler[1]=math.pi/2
    elif axis=='Y': o.rotation_euler[0]=math.pi/2
    if 'direction' in job: o.rotation_euler=Vector(job['direction']).to_track_quat('Z','Y').to_euler()
    if o.type=='MESH' and k not in ('sphere','torus','panel'):
        b=o.modifiers.new('Precision edge radius','BEVEL'); b.width=.035 if min(d)>.1 else .012; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if o.type=='MESH' and k in ('cyl','cone','sphere','torus'):
        for f in o.data.polygons: f.use_smooth=True
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    MESSAGE='Add: '+o.name; yield .10
    PARTS.append(o)
    FRAME += 3
    o.keyframe_insert(data_path='hide_viewport', frame=1); o.keyframe_insert(data_path='hide_render', frame=1)
    o.keyframe_insert(data_path='hide_viewport', frame=FRAME); o.keyframe_insert(data_path='hide_render', frame=FRAME)
    S.frame_set(FRAME); S.frame_end=FRAME
    MESSAGE='Finish: '+o.name; yield .08

def build_stage(stage):
    for job in JOBS[stage]: yield from construct(job, stage)

def tick():
    global BUSY, CURRENT, MESSAGE
    try:
        delay=next(ITER)
        for screen in bpy.data.screens:
            for ar in screen.areas: ar.tag_redraw()
        return delay
    except StopIteration:
        BUSY=False; CURRENT+=1; MESSAGE='Stage complete - inspect, then Build next'
        for o in bpy.context.selected_objects: o.select_set(False)
        return None
    except Exception as e:
        BUSY=False; MESSAGE='ERROR: '+str(e); print(MESSAGE); return None

def view_full():
    for ar in bpy.context.screen.areas:
        if ar.type=='VIEW_3D':
            v=ar.spaces.active; v.region_3d.view_location=(0,0,0); v.region_3d.view_distance=12
            v.region_3d.view_rotation=Vector((1.15,-1.7,.95)).to_track_quat('Z','Y')
            v.region_3d.view_perspective='ORTHO'; v.overlay.show_floor=False; v.overlay.show_axis_x=False; v.overlay.show_axis_y=False
            v.shading.type='MATERIAL'; v.shading.show_shadows=True; v.shading.show_cavity=True; v.shading.cavity_type='BOTH'

def view_structural():
    for o in PARTS:
        o.hide_set(False)
    view_full()

class ArkNext(bpy.types.Operator):
    bl_idname='ark.next'; bl_label='Build next stage'
    def execute(self, context):
        global ITER, BUSY, MESSAGE
        if BUSY: return {'CANCELLED'}
        if CURRENT>=7: finalize(); return {'FINISHED'}
        ITER=build_stage(CURRENT); BUSY=True; MESSAGE=STAGE_NAMES[CURRENT]
        bpy.app.timers.register(tick, first_interval=.25); return {'FINISHED'}

class ArkFull(bpy.types.Operator):
    bl_idname='ark.full'; bl_label='Full ship view'
    def execute(self, context): view_structural(); return {'FINISHED'}

class ArkCenter(bpy.types.Operator):
    bl_idname='ark.center'; bl_label='Center spine detail'
    def execute(self, context):
        for ar in bpy.context.screen.areas:
            if ar.type=='VIEW_3D':
                v=ar.spaces.active; v.region_3d.view_location=(0,0,0); v.region_3d.view_distance=5.6; v.region_3d.view_rotation=Vector((.65,-1.05,.25)).to_track_quat('Z','Y'); v.region_3d.view_perspective='ORTHO'
        return {'FINISHED'}

class ArkPanel(bpy.types.Panel):
    bl_label='ARK SHIP / LIVE BUILD'; bl_idname='ARK_PT_build'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='ARK Build'
    def draw(self, context):
        l=self.layout; l.label(text='STREAMLINED ARK SHIP'); l.label(text='Reference synthesis / form only'); l.separator()
        l.label(text=f'Stage {min(CURRENT+1,8)} / 8  |  {len(PARTS)} parts'); l.label(text=STAGE_NAMES[min(CURRENT,7)]); l.label(text=MESSAGE[:42])
        row=l.row(); row.enabled=not BUSY; row.operator('ark.next', text='Build next stage' if CURRENT<7 else 'Save completed ship', icon='PLAY')
        l.separator(); l.operator('ark.full'); l.operator('ark.center'); l.separator(); l.label(text='No textures / no background'); l.label(text='Concept form, not fabrication drawings')

def finalize():
    global CURRENT, MESSAGE
    CURRENT=8; S.frame_set(FRAME); S.frame_end=FRAME; view_full();
    S['Reference synthesis']='Central spine + ring structures + swept habitat shells + propulsion pods'
    S['Design status']='High-detail form study; texture-free and not manufacturing validated'
    notes=bpy.data.texts.get('ARK_SHIP_DESIGN_NOTES') or bpy.data.texts.new('ARK_SHIP_DESIGN_NOTES')
    notes.clear(); notes.write('ARK SHIP / STREAMLINED FORM STUDY\n\nReference synthesis: four supplied images.\nPrimary language: central spine, forward command ring, aft fusion ring, four swept habitat shells, axial truss, radiator and maneuver pods.\nScene contains only ship geometry, lights and camera; render film is transparent and no floor/background mesh is present.\nTexture work intentionally omitted.\n\nEngineering status: concept geometry only. Pressure vessels, thermal paths, structural loads, control systems, propulsion and manufacturability require separate validation.\n')
    src=bpy.data.texts.get('ark_ship_build.py') or bpy.data.texts.new('ark_ship_build.py'); src.clear(); src.write(open(os.path.join(ROOT,'ark_ship_build.py'),encoding='utf-8').read())
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    MESSAGE='Saved: ARK_SHIP.blend'
    with open(os.path.join(ROOT,'ARK_SHIP_parts.json'),'w',encoding='utf-8') as f:
        json.dump([{'name':o.name,'stage':o.get('assembly_stage',0),'material':o.data.materials[0].name} for o in PARTS], f, ensure_ascii=False, indent=2)

for cls in [ArkNext, ArkFull, ArkCenter, ArkPanel]: bpy.utils.register_class(cls)

def ready():
    for ar in bpy.context.screen.areas:
        if ar.type=='CONSOLE': ar.type='VIEW_3D'
    view_full(); return None
bpy.app.timers.register(ready, first_interval=.8)
print('ARK progressive builder ready. Use the ARK Build sidebar.')
