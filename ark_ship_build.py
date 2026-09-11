import bpy, math, os, json
from mathutils import Vector

ROOT = r'C:\Users\user\Desktop\3d test'
BLEND_PATH = os.path.join(ROOT, 'ARK_SHIP.blend')
SCENE_NAME = 'ARK SHIP | EXCELSIOR multi-angle reconstruction'

# Unregister the previous live-build panel when the script is re-run.
for _cls in [globals().get('ArkNext'), globals().get('ArkFull'), globals().get('ArkCenter'), globals().get('ArkPanel')]:
    if _cls:
        try: bpy.utils.unregister_class(_cls)
        except: pass

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for old in list(bpy.data.scenes):
    if old.name == SCENE_NAME:
        bpy.data.scenes.remove(old)
sc = bpy.data.scenes.new(SCENE_NAME)
bpy.context.window.scene = sc
sc.unit_settings.system = 'METRIC'
sc.unit_settings.length_unit = 'METERS'
sc.render.film_transparent = True

def mkmat(name, color, metallic=0.0, rough=.3, emission=None):
    m = bpy.data.materials.new('EXCELSIOR / ' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = rough
    if emission:
        p.inputs['Emission Color'].default_value = (*emission, 1)
        p.inputs['Emission Strength'].default_value = 2.5
    return m

MAT = {
    'Hull': mkmat('painted white alloy', (.57, .63, .67), .78, .23),
    'HullDark': mkmat('shadow alloy', (.07, .095, .115), .75, .25),
    'Frame': mkmat('machined titanium truss', (.23, .30, .34), .9, .18),
    'Carbon': mkmat('carbon structural brace', (.018, .028, .036), .45, .25),
    'Glass': mkmat('smoked habitat glazing', (.035, .12, .18), .55, .13),
    'Panel': mkmat('solar radiator panel', (.025, .095, .17), .55, .2),
    'Copper': mkmat('thermal copper', (.55, .22, .075), .85, .22),
    'Ceramic': mkmat('thermal ceramic', (.78, .81, .78), .25, .32),
    'Glow': mkmat('service light', (.30, .72, 1.0), .1, .16, (.16, .45, 1.0)),
    'Amber': mkmat('warm habitat light', (.9, .35, .07), .1, .2, (1.0, .12, .02)),
}

STAGE_NAMES = [
    '01 axial spine / pressure bulkheads',
    '02 command and docking module',
    '03 rear fusion / production module',
    '04 habitat arm internals',
    '05 four curved solar habitat shells',
    '06 central ring / diagonal truss',
    '07 cargo, sensors and service hardware',
    '08 final inspection and save',
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
MESSAGE = 'Ready: build reference-matched axial spine'
FRAME = 1

def add(stage, kind, name, p, dims, material='Hull', **kw):
    JOBS[stage].append(dict(kind=kind, name=name, p=tuple(p), dims=tuple(dims), material=material, **kw))
def box(st, name, p, dims, material='Hull', rot=(0,0,0), **kw): add(st, 'box', name, p, dims, material, rot=rot, **kw)
def cyl(st, name, p, radius, depth, material='Hull', axis='Z', **kw): add(st, 'cyl', name, p, (radius, depth), material, axis=axis, **kw)
def cone(st, name, p, r1, r2, depth, material='Hull', axis='Z', **kw): add(st, 'cone', name, p, (r1, r2, depth), material, axis=axis, **kw)
def torus(st, name, p, major, minor, material='Frame', axis='X', **kw): add(st, 'torus', name, p, (major, minor), material, axis=axis, **kw)
def sphere(st, name, p, radius, material='Hull', scale=(1,1,1), **kw): add(st, 'sphere', name, p, (radius,), material, scale=scale, **kw)
def rod(st, name, a, b, radius, material='Frame', **kw):
    a, b = Vector(a), Vector(b)
    add(st, 'rod', name, tuple((a+b)/2), (radius, (b-a).length), material, direction=tuple(b-a), **kw)
def cable(st, name, points, radius=.018, material='Copper', **kw): add(st, 'cable', name, points[0], (radius,), material, points=points, **kw)
def label(st, text, p, size=.13, material='Ceramic', rot=(math.pi/2,0,0), **kw): add(st, 'label', text, p, (size,), material, rot=rot, **kw)

# Normalized reference geometry: x is the 312 m longitudinal axis. The arm tips
# reach roughly 198 m in the y direction and 82 m in z in the supplied sheets.
def arm_point(u, base, twist=0.0, w=0.0):
    x = -4.05 + 8.65*u
    bulge = math.sin(math.pi * (u**0.90))**0.92
    radius = 0.98 + 3.20*bulge
    th = base + twist*(u-.5)
    half = 0.16 + 0.42*(math.sin(math.pi*u)**0.72)
    rr = radius + w*half
    return (x, rr*math.cos(th), rr*math.sin(th))

def arm_surface(st, name, base, twist, material='Hull'):
    add(st, 'arm_shell', name, (0,0,0), (.075,), material, base=base, twist=twist)

# ---- Stage 01: axial spine, pressure collars and utility bus ----
cyl(0, 'Primary pressure spine', (-.1,0,0), .44, 12.7, 'Hull', 'X')
cyl(0, 'Data and power bus', (.0,0,0), .27, 13.4, 'Carbon', 'X')
for x in [-5.35,-4.55,-3.55,-2.35,-1.15,0.15,1.45,2.75,4.05,5.15,6.0]:
    r = .62 if abs(x)<4.5 else .78
    torus(0, 'Spine pressure bulkhead', (x,0,0), r, .085, 'Frame', 'X')
    for a in range(0,360,45):
        q=math.radians(a)
        rod(0, 'Bulkhead radial brace', (x,0,0), (x,(r-.06)*math.cos(q),(r-.06)*math.sin(q)), .022, 'Carbon')
for side in [-1,1]:
    rod(0, 'Longitudinal utility conduit', (-4.9,side*.56,.18), (5.8,side*.56,.18), .028, 'Copper')
    rod(0, 'Longitudinal coolant conduit', (-4.9,side*.56,-.18), (5.8,side*.56,-.18), .025, 'Ceramic')
for x in [-4.6,-3.2,-1.8,-.4,1.0,2.4,3.8,5.2]:
    box(0, 'Spine service panel', (x,-.47,.0), (.48,.055,.28), 'HullDark')
    for y in [-.52,.52]: sphere(0, 'Spine fastener', (x,y,.22), .035, 'Ceramic')
label(0, 'EXCELSIOR / AXIAL SPINE', (0,-.32,.50), .12)

# ---- Stage 02: forward command / docking module ----
cyl(1, 'Command pressure drum', (-6.05,0,0), 1.20, 1.35, 'Hull', 'X')
cone(1, 'Command aerodynamic nose', (-7.20,0,0), 1.15, .18, 1.65, 'Hull', 'X')
torus(1, 'Command outer frame', (-6.55,0,0), 1.27, .13, 'Frame', 'X')
torus(1, 'Docking interface ring', (-7.65,0,0), .38, .09, 'Frame', 'X')
cyl(1, 'Forward sensor barrel', (-7.92,0,0), .20, .35, 'Glass', 'X')
rod(1, 'Forward sensor mast', (-8.05,0,0), (-8.55,0,0), .035, 'Frame')
for a in range(0,360,45):
    q=math.radians(a)
    rod(1, 'Command ring spoke', (-6.72,0,0), (-6.72,1.10*math.cos(q),1.10*math.sin(q)), .025, 'Carbon')
for a in [-55,-28,0,28,55]:
    q=math.radians(a)
    y,z=1.05*math.sin(q),1.05*math.cos(q)
    box(1, 'Bridge window frame', (-6.20,y,z), (.18,.22,.16), 'Frame')
    box(1, 'Bridge window', (-6.08,y,z), (.035,.15,.09), 'Glass')
for side in [-1,1]:
    box(1, 'Docking avionics box', (-5.30,side*.92,.0), (.56,.28,.40), 'HullDark')
    torus(1, 'Docking collar', (-5.0,side*1.08,0), .28, .05, 'Frame', 'Y')
label(1, 'COMMAND / DOCKING', (-6.2,-1.28,.30), .115)

# ---- Stage 03: aft fusion reactor and manufacturing module ----
cyl(2, 'Rear production pressure shell', (5.70,0,0), 1.24, 1.65, 'HullDark', 'X')
torus(2, 'Rear structural ring', (4.88,0,0), 1.38, .15, 'Frame', 'X')
torus(2, 'Reactor containment ring', (6.36,0,0), 1.15, .14, 'Copper', 'X')
cone(2, 'Fusion exhaust bell', (6.85,0,0), 1.05, .56, 1.10, 'HullDark', 'X')
cyl(2, 'Fusion throat', (7.48,0,0), .42, .26, 'Glow', 'X')
for a in range(0,360,45):
    q=math.radians(a)
    rod(2, 'Reactor shield brace', (5.05,0,0), (5.05,1.28*math.cos(q),1.28*math.sin(q)), .032, 'Frame')
for side in [-1,1]:
    box(2, 'Production bay module', (5.65,side*.92,.05), (.72,.34,.42), 'Hull')
    box(2, 'Production radiator', (6.30,side*.88,.05), (.55,.08,.42), 'Panel')
    for z in [-.22,0,.22]: box(2, 'Reactor service strip', (5.65,side*1.13,z), (.42,.035,.035), 'Copper')
label(2, 'REAR PROPULSION / PRODUCTION', (5.7,-1.28,.28), .105)

# ---- Stage 04: habitat arm internals and root trusses ----
ARM_BASES = [0, math.pi/2, math.pi, 3*math.pi/2]
ARM_NAMES = ['starboard', 'upper', 'port', 'lower']
for base, arm_name in zip(ARM_BASES, ARM_NAMES):
    twist = math.radians(10 if arm_name in ('upper','lower') else -10)
    for u in [.08,.48,.90]:
        p = arm_point(u,base,twist,0)
        rod(3, f'{arm_name} arm lower truss', (p[0],p[1]*.90,p[2]*.90), (p[0],p[1],p[2]), .032, 'Frame')
    for u in [.16,.36,.56,.76]:
        p = arm_point(u,base,twist,0)
        box(3, f'{arm_name} habitat pressure module', (p[0],p[1]*.89,p[2]*.89), (.72,.34,.28), 'HullDark')
        box(3, f'{arm_name} habitat glazing', (p[0],p[1]*.96,p[2]*.96), (.46,.04,.18), 'Glass')
        for dx in [-.20,0,.20]:
            sphere(3, f'{arm_name} habitat window light', (p[0]+dx,p[1]*.985,p[2]*.985), .035, 'Amber')
    for u in [.28,.72]:
        p=arm_point(u,base,twist,0)
        rod(3, f'{arm_name} diagonal support', (p[0],0,0), p, .045, 'Frame')
    label(3, f'HABITAT ARM / {arm_name.upper()}', arm_point(.48,base,twist,0), .085, 'Ceramic')

# ---- Stage 05: four independent curved habitat / solar shells ----
for base, arm_name in zip(ARM_BASES, ARM_NAMES):
    twist = math.radians(10 if arm_name in ('upper','lower') else -10)
    arm_surface(4, f'{arm_name} curved habitat shell', base, twist, 'Hull')
    for w in [-1,1]:
        for u0,u1 in [(0.035,.20),(.20,.38),(.38,.56),(.56,.74),(.74,.92),(.92,.975)]:
            rod(4, f'{arm_name} shell edge rail', arm_point(u0,base,twist,w), arm_point(u1,base,twist,w), .034, 'Frame')
    for u in [.12,.25,.38,.51,.64,.77,.90]:
        rod(4, f'{arm_name} solar panel rib', arm_point(u,base,twist,-1), arm_point(u,base,twist,1), .024, 'Carbon')
        p=arm_point(u,base,twist,.55)
        box(4, f'{arm_name} panel seam', (p[0],p[1]*1.004,p[2]*1.004), (.035,.11,.11), 'Panel')
    rod(4, f'{arm_name} shell center spar', arm_point(.05,base,twist,0), arm_point(.95,base,twist,0), .052, 'Frame')
    p0=arm_point(.02,base,twist,0); p1=arm_point(.08,base,twist,0)
    rod(4, f'{arm_name} root hinge', p0, p1, .095, 'Copper')
    pt=arm_point(.975,base,twist,0)
    cone(4, f'{arm_name} tapered shell tip', pt, .12, .015, .38, 'Hull', 'X')

# ---- Stage 06: central ring hub, bearing and truss connections ----
torus(5, 'Central rotation ring outer', (.25,0,0), 1.72, .16, 'Frame', 'X')
torus(5, 'Central rotation ring inner', (.25,0,0), 1.42, .07, 'Copper', 'X')
cyl(5, 'Central ring pressure hub', (.25,0,0), .72, .88, 'Hull', 'X')
for a in range(0,360,45):
    q=math.radians(a)
    rod(5, 'Central ring radial truss', (.25,0,0), (.25,1.60*math.cos(q),1.60*math.sin(q)), .035, 'Frame')
for base, arm_name in zip(ARM_BASES, ARM_NAMES):
    twist = math.radians(10 if arm_name in ('upper','lower') else -10)
    for u in [.42,.60]:
        p=arm_point(u,base,twist,0)
        rod(5, 'Central ring to habitat strut', (.25,0,0), p, .055, 'Frame')
for side in [-1,1]:
    box(5, 'Ring utility transfer box', (.25,side*1.10,.18), (.44,.26,.34), 'HullDark')
    box(5, 'Ring access hatch', (.25,side*1.47,.0), (.24,.06,.26), 'Glass')
label(5, 'CENTRAL RING / ROTATION INTERFACE', (.25,-1.86,.10), .105)

# ---- Stage 07: cargo / utility pods, antennas and precision details ----
for side in [-1,1]:
    for x in [-3.45,-2.45,-1.45]:
        box(6, 'Cargo utility pod', (x,side*.88,.52), (.72,.42,.44), 'HullDark')
        box(6, 'Cargo pod blue panel', (x,side*1.10,.52), (.42,.035,.25), 'Panel')
        for z in [.38,.52,.66]: box(6, 'Cargo pod service line', (x,side*1.125,z), (.30,.02,.018), 'Copper')
for x in [-4.2,-3.3,-2.4,-1.5,-.6,.3,1.2,2.1,3.0,3.9]:
    box(6, 'Spine maintenance hatch', (x,0,.54), (.34,.34,.08), 'Hull')
    for side in [-1,1]:
        cable(6, 'External service cable', [(x-.25,side*.62,.42),(x,side*.72,.48),(x+.25,side*.62,.42)], .014, 'Copper')
for base, arm_name in zip(ARM_BASES, ARM_NAMES):
    twist = math.radians(10 if arm_name in ('upper','lower') else -10)
    for u in [.25,.52,.79]:
        p=arm_point(u,base,twist,.36)
        box(6, f'{arm_name} exterior utility rack', (p[0],p[1]*1.01,p[2]*1.01), (.30,.16,.18), 'HullDark')
        sphere(6, f'{arm_name} navigation marker', (p[0],p[1]*1.02,p[2]*1.02), .045, 'Glow')
rod(6, 'Navigation antenna mast', (2.55,0,.62), (2.55,0,1.75), .026, 'Frame')
sphere(6, 'Navigation antenna head', (2.55,0,1.82), .11, 'Glass')
for x in [-6.65,6.0]:
    torus(6, 'Lidar guard', (x,0,0), .30, .045, 'Frame', 'X')
    sphere(6, 'Lidar lens', (x,0,0), .16, 'Glass', scale=(.55,1,1))
label(6, 'EXT. THE EXCELSIOR / TECHNICAL FORM STUDY', (0,-.38,-.62), .095)

# ---- mesh constructors ----
def arm_mesh(base,twist):
    verts=[]; faces=[]; nx=33; nw=11
    for i in range(nx):
        u=i/(nx-1)
        for j in range(nw):
            w=-1+2*j/(nw-1); verts.append(arm_point(u,base,twist,w))
    for i in range(nx-1):
        for j in range(nw-1):
            a=i*nw+j; faces.append((a,a+1,a+nw+1,a+nw))
    me=bpy.data.meshes.new('curved habitat shell mesh'); me.from_pydata(verts,[],faces); me.update(); return me

def construct(job, stage):
    global FRAME, MESSAGE
    k=job['kind']; p=job['p']; d=job['dims']; o=None
    if k=='box':
        bpy.ops.mesh.primitive_cube_add(size=1, location=p); o=bpy.context.object; o.dimensions=d; o.rotation_euler=job.get('rot',(0,0,0)); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    elif k=='cyl':
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=d[0],depth=d[1],location=p); o=bpy.context.object
    elif k=='cone':
        bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=d[0],radius2=d[1],depth=d[2],location=p); o=bpy.context.object
    elif k=='torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=d[0],minor_radius=d[1],major_segments=64,minor_segments=16,location=p); o=bpy.context.object
    elif k=='sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=d[0],location=p); o=bpy.context.object; o.scale=job.get('scale',(1,1,1))
    elif k=='rod':
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=d[0],depth=d[1],location=p); o=bpy.context.object
    elif k=='arm_shell':
        o=bpy.data.objects.new(job['name'],arm_mesh(job['base'],job['twist'])); sc.collection.objects.link(o); sol=o.modifiers.new('habitat shell thickness','SOLIDIFY'); sol.thickness=d[0]; bev=o.modifiers.new('aerodynamic edge radius','BEVEL'); bev.width=.035; bev.segments=3
    elif k=='cable':
        cu=bpy.data.curves.new(job['name'],'CURVE'); cu.dimensions='3D'; cu.bevel_depth=d[0]; cu.bevel_resolution=4; sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(job['points'])-1)
        for bp,q in zip(sp.bezier_points,job['points']): bp.co=q; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
        o=bpy.data.objects.new(job['name'],cu); sc.collection.objects.link(o)
    elif k=='label':
        cu=bpy.data.curves.new(job['name'],'FONT'); cu.body=job['name']; cu.align_x='CENTER'; cu.size=d[0]; cu.extrude=.003; o=bpy.data.objects.new(job['name'],cu); sc.collection.objects.link(o); o.location=p; o.rotation_euler=job.get('rot',(0,0,0))
    else: return
    o.name=job['name']; o.data.materials.append(MAT[job['material']]); o['assembly_stage']=stage+1; o['design_note']='Multi-angle reference reconstruction; form study only'
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[stage].objects.link(o)
    axis=job.get('axis','Z')
    if axis=='X': o.rotation_euler[1]=math.pi/2
    elif axis=='Y': o.rotation_euler[0]=math.pi/2
    if 'direction' in job: o.rotation_euler=Vector(job['direction']).to_track_quat('Z','Y').to_euler()
    if o.type=='MESH' and k not in ('sphere','torus','arm_shell'):
        b=o.modifiers.new('precision edge radius','BEVEL'); b.width=.032 if min(d)>.1 else .012; b.segments=3; o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    if o.type=='MESH' and k in ('cyl','cone','sphere','torus'):
        for f in o.data.polygons: f.use_smooth=True
    PARTS.append(o); FRAME += 2
    o.keyframe_insert(data_path='hide_viewport',frame=1); o.keyframe_insert(data_path='hide_render',frame=1); o.keyframe_insert(data_path='hide_viewport',frame=FRAME); o.keyframe_insert(data_path='hide_render',frame=FRAME)
    S.frame_set(FRAME); S.frame_end=FRAME; MESSAGE='Finish: '+o.name; yield .045

def build_stage(stage):
    for job in JOBS[stage]: yield from construct(job,stage)

def tick():
    global BUSY,CURRENT,MESSAGE
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
            v=ar.spaces.active; v.region_3d.view_location=(0,0,0); v.region_3d.view_distance=17; v.region_3d.view_rotation=Vector((1.2,-1.65,.95)).to_track_quat('Z','Y'); v.region_3d.view_perspective='ORTHO'; v.overlay.show_floor=False; v.overlay.show_axis_x=False; v.overlay.show_axis_y=False; v.shading.type='MATERIAL'; v.shading.show_shadows=True; v.shading.show_cavity=True; v.shading.cavity_type='BOTH'
def view_top():
    for ar in bpy.context.screen.areas:
        if ar.type=='VIEW_3D':
            v=ar.spaces.active; v.region_3d.view_location=(0,0,0); v.region_3d.view_distance=17; v.region_3d.view_rotation=Vector((0,0,1)).to_track_quat('Z','Y'); v.region_3d.view_perspective='ORTHO'
def view_side():
    for ar in bpy.context.screen.areas:
        if ar.type=='VIEW_3D':
            v=ar.spaces.active; v.region_3d.view_location=(0,0,0); v.region_3d.view_distance=17; v.region_3d.view_rotation=Vector((0,1,0)).to_track_quat('Z','Y'); v.region_3d.view_perspective='ORTHO'
def view_structural():
    for o in PARTS: o.hide_set(False)
    view_full()

class ArkNext(bpy.types.Operator):
    bl_idname='ark.next'; bl_label='Build next stage'
    def execute(self,context):
        global ITER,BUSY,MESSAGE
        if BUSY: return {'CANCELLED'}
        if CURRENT>=7: finalize(); return {'FINISHED'}
        ITER=build_stage(CURRENT); BUSY=True; MESSAGE=STAGE_NAMES[CURRENT]; bpy.app.timers.register(tick,first_interval=.20); return {'FINISHED'}
class ArkFull(bpy.types.Operator):
    bl_idname='ark.full'; bl_label='Full perspective view'
    def execute(self,context): view_structural(); return {'FINISHED'}
class ArkCenter(bpy.types.Operator):
    bl_idname='ark.center'; bl_label='Central ring detail'
    def execute(self,context):
        for ar in bpy.context.screen.areas:
            if ar.type=='VIEW_3D':
                v=ar.spaces.active; v.region_3d.view_location=(.25,0,0); v.region_3d.view_distance=6.5; v.region_3d.view_rotation=Vector((.8,-1.1,.35)).to_track_quat('Z','Y'); v.region_3d.view_perspective='ORTHO'
        return {'FINISHED'}
class ArkPanel(bpy.types.Panel):
    bl_label='EXCELSIOR / LIVE BUILD'; bl_idname='ARK_PT_build'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='ARK Build'
    def draw(self,context):
        l=self.layout; l.label(text='EXCELSIOR / MULTI-ANGLE REBUILD'); l.label(text='312 m axis / 4 habitat arms'); l.separator(); l.label(text=f'Stage {min(CURRENT+1,8)} / 8  |  {len(PARTS)} parts'); l.label(text=STAGE_NAMES[min(CURRENT,7)]); l.label(text=MESSAGE[:38]); row=l.row(); row.enabled=not BUSY; row.operator('ark.next',text='Build next stage' if CURRENT<7 else 'Save completed ship',icon='PLAY'); l.separator(); l.operator('ark.full'); l.operator('ark.center'); l.separator(); l.label(text='Texture-free form study'); l.label(text='No background / no floor mesh')

def finalize():
    global CURRENT,MESSAGE
    CURRENT=8; S.frame_set(FRAME); S.frame_end=FRAME; view_full(); S['Reference']='Four supplied Excelsior multi-angle sheets'; S['Proportions']='312 m overall / 198 m arm span / 82 m height'; S['Design status']='High-detail reference reconstruction; no textures; concept geometry only'
    notes=bpy.data.texts.get('EXCELSIOR_DESIGN_NOTES') or bpy.data.texts.new('EXCELSIOR_DESIGN_NOTES'); notes.clear(); notes.write('EXCELSIOR / ARK SHIP MULTI-ANGLE RECONSTRUCTION\n\nReference basis: four supplied orthographic, exploded and component sheets.\nStructure: axial pressure spine, command/docking module, rear fusion/production module, four independent curved habitat/solar arms, central rotation ring and diagonal truss.\nProportions normalized from the reference labels: 312 m overall length, 198 m arm span, 82 m overall height.\nTexture work intentionally omitted; panel seams, frames, windows and service hardware are geometry.\nEngineering status: visual concept geometry only; pressure, thermal, structural and propulsion validation remain separate work.\n')
    src=bpy.data.texts.get('ark_ship_build.py') or bpy.data.texts.new('ark_ship_build.py'); src.clear(); src.write(open(os.path.join(ROOT,'ark_ship_build.py'),encoding='utf-8').read())
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH); MESSAGE='Saved: ARK_SHIP.blend'
    with open(os.path.join(ROOT,'ARK_SHIP_parts.json'),'w',encoding='utf-8') as f: json.dump([{'name':o.name,'stage':o.get('assembly_stage',0),'material':o.data.materials[0].name} for o in PARTS],f,ensure_ascii=False,indent=2)

for cls in [ArkNext,ArkFull,ArkCenter,ArkPanel]: bpy.utils.register_class(cls)
def ready():
    for ar in bpy.context.screen.areas:
        if ar.type=='CONSOLE': ar.type='VIEW_3D'
    view_full(); return None
bpy.app.timers.register(ready,first_interval=.8)
print('EXCELSIOR multi-angle progressive builder ready. Use the ARK Build sidebar.')

