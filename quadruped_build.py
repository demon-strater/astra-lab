import bpy, math, json, os
from mathutils import Vector

# Progressive, visible assembly. Each timer tick makes one modelling change.
ROOT = r'C:\Users\user\Desktop\3d test'
S = bpy.context.scene
S.name = 'Q4 | Industrial inspection - engineering concept'
S.unit_settings.system = 'METRIC'
S.unit_settings.length_unit = 'MILLIMETERS'
M = {}
for name, color, metallic in [
    ('Aluminium', (.43,.49,.53), .8), ('Graphite',(.075,.085,.095),.65),
    ('Carbon',(.025,.035,.042),.35), ('Rubber',(.016,.019,.021),0),
    ('Safety',(.62,.43,.055),.45), ('Copper',(.56,.22,.075),.75),
    ('PCB',(.018,.16,.095),.1), ('Blue',(.045,.17,.31),.25),
    ('Red',(.48,.025,.018),.1), ('Lens',(.025,.14,.2),.7),
    ('White',(.76,.79,.78),.2)]:
    m=bpy.data.materials.new('Q4 / '+name); m.diffuse_color=(*color,1)
    m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=.33
    M[name]=m

NAMES=['01 Chassis / machined frame','02 Abduction / four hip modules',
       '03 Pitch drives / internal components','04 Upper links / load paths',
       '05 Knees, lower links and feet','06 Battery, compute and harness',
       '07 Service covers and sensors','08 Inspection and saved views']
COL=[]
for n in NAMES:
    c=bpy.data.collections.new(n); S.collection.children.link(c); COL.append(c)
JOBS=[[] for _ in NAMES]
CURRENT=0; BUSY=False; ITER=None; MESSAGE='Ready: build the chassis'
COUNT=0; FRAME=1; SHELL=[]; OBJS=[]

def add(stage, kind, name, p, d, material='Aluminium', **kw):
    JOBS[stage].append(dict(kind=kind,name=name,p=p,d=d,material=material,**kw))
def box(st,n,p,d,m='Aluminium',**kw):add(st,'box',n,p,d,m,**kw)
def cyl(st,n,p,r,h,m='Aluminium',axis='Z',**kw):add(st,'cyl',n,p,(r,h),m,axis=axis,**kw)
def ring(st,n,p,r,t,h,m='Aluminium',axis='Y',cut=False,**kw):add(st,'ring',n,p,(r,t,h),m,axis=axis,cut=cut,**kw)
def rod(st,n,a,b,r,m='Aluminium'):
    a,b=Vector(a),Vector(b); add(st,'rod',n,tuple((a+b)/2),(r,(b-a).length),m,direction=tuple(b-a))
def cable(st,n,pts,r=.003,m='Rubber'):add(st,'cable',n,pts[0],(r,),m,points=pts)
def label(st,n,p,size=.018,rot=(0,0,0),m='White'):add(st,'label',n,p,(size,),m,rot=rot)

# 800 x 360 mm load-bearing chassis. No solid block concealing the internals.
for y in [-.165,.165]:
    box(0,'Longitudinal extrusion',(0,y,.565),(.80,.026,.072))
    box(0,'Extrusion relief channel',(0,y-.014 if y<0 else y+.014,.57),(.70,.003,.018),'Graphite')
for x in [-.37,-.2,0,.2,.37]:
    box(0,'Transverse rib',(x,0,.554),(.016,.31,.046))
box(0,'Lower service tray',(0,0,.524),(.76,.31,.009),'Graphite')
for x in [-.365,.365]:
    for y in [-.153,.153]:
        box(0,'Hip mounting block',(x,y,.587),(.07,.06,.08))
        for dx in [-.02,.02]:cyl(0,'M6 mounting bolt',(x+dx,y,.632),.0045,.005,'Graphite')
label(0,'Q4 / CHASSIS 800',(0,-.181,.57),.018,(math.pi/2,0,0))

LEGS=[]
for x,front in [(.30,'F'),(-.30,'R')]:
    for side,letter in [(-1,'L'),(1,'R')]:
        tag=front+letter
        hip=(x,side*.245,.59); pitch=(x,side*.298,.565)
        knee=(x+.135,side*.315,.335); foot=(x-.012,side*.333,.046)
        LEGS.append((tag,side,hip,pitch,knee,foot))
        cyl(1,tag+' HAA motor body',hip,.053,.079,'Graphite','X')
        for dx in [-.04,.04]:ring(1,tag+' HAA flange',(x+dx,hip[1],hip[2]),.055,.006,.009,axis='X')
        for i in range(8):
            a=i*math.tau/8
            cyl(1,tag+' HAA cover screw',(x+.047,hip[1]+.043*math.cos(a),hip[2]+.043*math.sin(a)),.003,.005,'Graphite','X')
        box(1,tag+' Hip offset yoke',(x,side*.277,.552),(.045,.10,.032))
        cyl(1,tag+' HAA output shaft',(x,side*.285,.59),.012,.075,'Aluminium','X')
        # Pitch actuator is an illustrative coaxial BLDC + planetary stack.
        cy=side*.302
        cut=(tag=='FL')
        ring(2,tag+' HFE casing',(x,cy,.565),.062,.005,.065,'Graphite',cut=cut)
        ring(2,tag+' Stator lamination',(x,cy-.013*side,.565),.054,.010,.025,'Aluminium',cut=cut)
        for i in range(12):
            a=i*math.tau/12
            if cut and math.sin(a)>.3:continue
            cyl(2,tag+' Copper winding',(x+.043*math.cos(a),cy-.014*side,.565+.043*math.sin(a)),.007,.023,'Copper','Y')
        cyl(2,tag+' Rotor hub',(x,cy-.012*side,.565),.029,.025,'Graphite','Y')
        cyl(2,tag+' Rotor shaft',(x,cy,.565),.009,.080,'Aluminium','Y')
        ring(2,tag+' Reducer annulus',(x,cy+.023*side,.565),.053,.006,.015,'Aluminium',cut=cut)
        cyl(2,tag+' Sun gear',(x,cy+.023*side,.565),.011,.016,'Aluminium','Y')
        for i in range(3):
            a=i*math.tau/3
            gx=x+.027*math.cos(a); gz=.565+.027*math.sin(a)
            cyl(2,tag+' Planet gear',(gx,cy+.023*side,gz),.015,.016,'Graphite','Y')
            cyl(2,tag+' Planet pin',(gx,cy+.034*side,gz),.004,.008,'Aluminium','Y')
        ring(2,tag+' Output bearing',(x,cy+.039*side,.565),.034,.006,.008,'Aluminium')
        if cut:
            for i in range(16):
                a=i*math.tau/16
                add(2,'sphere',tag+' Bearing ball',(x+.03*math.cos(a),cy+.039*side,.565+.03*math.sin(a)),(.0027,),'Aluminium')
        ring(2,tag+' Encoder PCB',(x,cy-.038*side,.565),.027,.006,.003,'PCB')
        # Paired structural side plates with a hollow centre.
        for offset in [-.022,.022]:
            a=Vector(pitch); b=Vector(knee);a.y+=offset;b.y+=offset
            add(3,'link',tag+' Upper link side plate',tuple((a+b)/2),(.042,.008,(b-a).length),'Aluminium',direction=tuple(b-a))
        rod(3,tag+' Upper link carbon spine',pitch,knee,.017,'Carbon')
        for u in [.24,.76]:
            p=Vector(pitch).lerp(Vector(knee),u)
            cyl(3,tag+' Upper link spacer',tuple(p),.009,.052,'Graphite','Y')
        cable(3,tag+' Motor cable',[tuple(Vector(pitch)+Vector((-.03,-.02*side,0))), (x+.018,side*.28,.45),tuple(Vector(knee)+Vector((-.025,-.02*side,.02)))],.004)
        cyl(4,tag+' KFE sealed actuator',knee,.044,.069,'Graphite','Y')
        for dy in [-.038,.038]:ring(4,tag+' KFE bearing cover',(knee[0],knee[1]+dy,knee[2]),.045,.007,.007)
        for i in range(6):
            a=i*math.tau/6
            cyl(4,tag+' Knee fastener',(knee[0]+.034*math.cos(a),knee[1]+side*.043,knee[2]+.034*math.sin(a)),.0027,.004,'Graphite','Y')
        rod(4,tag+' Carbon lower leg',knee,foot,.017,'Carbon')
        for t in [.12,.88]:
            p=Vector(knee).lerp(Vector(foot),t)
            add(4,'rod',tag+' Lower leg clamp',tuple(p),(.023,.028),'Aluminium',direction=tuple(Vector(foot)-Vector(knee)))
        cyl(4,tag+' Foot loadcell',(foot[0],foot[1],.058),.022,.027,'Aluminium')
        add(4,'sphere',tag+' Elastomer contact foot',(foot[0],foot[1],.028),(.034,),'Rubber',scale=(1,1,.82))
        for j in [-1,0,1]:box(4,tag+' Sole tread',(foot[0]+j*.015,foot[1],.009),(.007,.045,.006),'Graphite')
        label(4,tag,(knee[0]-.009,knee[1]+side*.049,knee[2]-.006),.016,(math.pi/2 if side<0 else -math.pi/2,0,0))

# Internal pack, electrical separation, restrained harnesses and cooling.
box(5,'Battery isolation cradle',(-.13,0,.554),(.32,.258,.018),'Rubber')
for i in range(12):
    for j in range(4):
        cyl(5,'Illustrative cylindrical cell',(-.267+i*.025,-.038+j*.025,.597),.0105,.068,'Blue')
for i in range(12):box(5,'Cell interconnect strip',(-.267+i*.025,0,.633),(.010,.10,.0015),'Copper')
for x in [-.25,-.05]:box(5,'Battery retention strap',(x,0,.638),(.018,.13,.004),'Graphite')
box(5,'Battery BMS PCB',(-.13,.10,.609),(.25,.043,.008),'PCB')
for i in range(6):box(5,'BMS balancing IC',(-.22+i*.035,.10,.617),(.018,.02,.009),'Graphite')
box(5,'Fused power distribution',(.085,-.073,.567),(.065,.10,.028),'Graphite')
box(5,'Main DC fuse',(.085,-.075,.588),(.033,.065,.013),'Red')
box(5,'Compute carrier PCB',(.24,0,.558),(.21,.255,.008),'PCB')
box(5,'Compute module',(.225,.025,.579),(.095,.085,.027),'Graphite')
box(5,'Compute heatsink',(.225,.025,.599),(.11,.10,.012),'Aluminium')
for i in range(10):box(5,'Heatsink fin',(.178+i*.0105,.025,.614),(.003,.10,.022),'Aluminium')
for x in [.17,.23,.29]:box(5,'I/O connector',(x,-.112,.575),(.033,.025,.025),'Aluminium')
box(5,'IMU vibration isolator',(.01,.08,.56),(.048,.044,.011),'Rubber')
box(5,'IMU PCB',(.01,.08,.571),(.038,.034,.007),'PCB')
box(5,'IMU package',(.01,.08,.578),(.013,.013,.006),'Graphite')
for side in [-1,1]:
    cable(5,'Main protected bus loom',[(-.27,side*.14,.584),(-.1,side*.14,.58),(.1,side*.14,.58),(.31,side*.14,.588)],.005)
    for x in [-.25,-.12,.10,.25]:box(5,'Harness P clamp',(x,side*.14,.583),(.012,.018,.014),'Graphite')
    for x in [-.30,.30]:cable(5,'Hip branch harness',[(x,side*.13,.59),(x-.045,side*.18,.615),(x-.045,side*.235,.602)],.004)
cable(5,'Battery positive lead',[(-.04,-.04,.63),(.015,-.045,.632),(.045,-.074,.588)],.004,'Red')
cable(5,'Battery negative lead',[(-.04,-.015,.63),(.02,-.022,.624),(.05,-.042,.578)],.004,'Rubber')
label(5,'BATTERY MODULE',(-.15,0,.648),.014)
label(5,'COMPUTE',(.23,.028,.629),.013)

for side in [-1,1]:
    box(6,'Removable side protection',(0,side*.185,.578),(.70,.008,.087),'Safety',shell=True)
    for x in [-.32,-.12,.12,.32]:cyl(6,'Captive side screw',(x,side*.192,.60),.0035,.004,'Graphite','Y',shell=True)
    for i in range(8):box(6,'Side cooling grille',(.15+i*.023,side*.191,.56),(.012,.006,.028),'Graphite',shell=True)
box(6,'Removable upper service lid',(0,0,.666),(.77,.348,.014),'Graphite',shell=True)
for x in [-.32,.32]:
    for y in [-.14,.14]:cyl(6,'Lid captive screw',(x,y,.676),.004,.004,'Aluminium',shell=True)
for x in [-.23,.23]:
    for y in [-.13,.13]:box(6,'Payload mounting boss',(x,y,.682),(.033,.03,.023),'Aluminium',shell=True)
box(6,'Front sensor bulkhead',(.405,0,.592),(.023,.31,.115),'Graphite')
box(6,'Stereo sensor bar',(.421,0,.609),(.023,.237,.040),'Aluminium')
for y in [-.093,.093]:
    cyl(6,'Stereo optical bezel',(.437,y,.61),.016,.013,'Graphite','X')
    cyl(6,'Stereo lens',(.445,y,.61),.012,.005,'Lens','X')
box(6,'Depth projector',(.44,0,.61),(.008,.042,.02),'Lens')
cyl(6,'Lidar pedestal',(.18,0,.698),.049,.042,'Aluminium',shell=True)
cyl(6,'Lidar optical window',(.18,0,.735),.054,.037,'Lens',shell=True)
cyl(6,'Lidar cap',(.18,0,.758),.054,.009,'Graphite',shell=True)
cyl(6,'Emergency stop base',(-.28,0,.685),.026,.018,'Safety',shell=True)
cyl(6,'Emergency stop mushroom',(-.28,0,.702),.024,.017,'Red',shell=True)
label(6,'Q4  /  FIELD INSPECTION',(0,-.192,.578),.022,(math.pi/2,0,0),shell=True) if False else None
add(6,'label','Q4 / FIELD INSPECTION',(0,-.193,.578),(.018,),'Graphite',rot=(math.pi/2,0,0),shell=True)
box(6,'Rear connector panel',(-.406,0,.59),(.017,.265,.093),'Graphite')
for y in [-.07,0,.07]:cyl(6,'Sealed rear service connector',(-.42,y,.587),.012,.02,'Aluminium','X')

def make_ring(r,t,h,cut):
    verts=[]; faces=[]; seg=48
    start=.15*math.pi if cut else 0; end=1.85*math.pi if cut else math.tau
    for i in range(seg+1):
        a=start+(end-start)*i/seg
        for z,rr in [(-h/2,r),(-h/2,r-t),(h/2,r),(h/2,r-t)]:verts.append((rr*math.cos(a),rr*math.sin(a),z))
    for i in range(seg):
        a=4*i;b=a+4
        faces.extend([(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a,a+1,b+1,b),(a+2,b+2,b+3,a+3)])
    faces.extend([(0,2,3,1),(4*seg,4*seg+1,4*seg+3,4*seg+2)])
    mesh=bpy.data.meshes.new('Machined annular mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    return mesh

def construct(j,stage):
    global COUNT, FRAME, MESSAGE
    k=j['kind'];p=j['p'];d=j['d']
    for ob in bpy.context.selected_objects:ob.select_set(False)
    if k in ('box','link'):
        bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object
        o.scale=tuple(v*.4 for v in d)
    elif k in ('cyl','rod'):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=d[0],depth=d[1],location=p);o=bpy.context.object
    elif k=='sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=d[0],location=p);o=bpy.context.object
        o.scale=j.get('scale',(1,1,1))
    elif k=='ring':
        o=bpy.data.objects.new(j['name'],make_ring(*d,j.get('cut',False)));S.collection.objects.link(o);o.location=p
    elif k=='label':
        cu=bpy.data.curves.new(j['name'],'FONT');cu.body=j['name'];cu.align_x='CENTER';cu.size=d[0];cu.extrude=.0002
        o=bpy.data.objects.new(j['name'],cu);S.collection.objects.link(o);o.location=p;o.rotation_euler=j.get('rot',(0,0,0))
    else:
        cu=bpy.data.curves.new(j['name'],'CURVE');cu.dimensions='3D';cu.bevel_depth=d[0];cu.bevel_resolution=3
        sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(j['points'])-1)
        for q,v in zip(sp.bezier_points,j['points']):q.co=v;q.handle_left_type='AUTO';q.handle_right_type='AUTO'
        o=bpy.data.objects.new(j['name'],cu);S.collection.objects.link(o)
    o.name=j['name'];o.data.materials.append(M[j['material']]);o['assembly_stage']=stage+1
    o['engineering_status']='Visual packaging concept; not manufacturing validated'
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[stage].objects.link(o)
    axis=j.get('axis','Z')
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    if 'direction' in j:o.rotation_euler=Vector(j['direction']).to_track_quat('Z','Y').to_euler()
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    MESSAGE='Add: '+o.name;yield .16
    if k in ('box','link'):
        o.scale=d;MESSAGE='Size: '+o.name;yield .16
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if o.type=='MESH' and k!='sphere':
        b=o.modifiers.new('Edge break / machining radius','BEVEL');b.width=min(.002,min(d)*.15);b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if o.type=='MESH' and k in ('sphere','cyl','rod','ring'):
        for f in o.data.polygons:f.use_smooth=True
    o['build_order']=COUNT;COUNT+=1;OBJS.append(o)
    if j.get('shell'):SHELL.append(o)
    # Save a replayable assembly sequence in the actual Blender timeline.
    o.hide_viewport=True;o.hide_render=True
    o.keyframe_insert(data_path='hide_viewport',frame=1);o.keyframe_insert(data_path='hide_render',frame=1)
    FRAME+=4
    o.hide_viewport=False;o.hide_render=False
    o.keyframe_insert(data_path='hide_viewport',frame=FRAME);o.keyframe_insert(data_path='hide_render',frame=FRAME)
    S.frame_set(FRAME);S.frame_end=FRAME
    MESSAGE='Finish: '+o.name;yield .12

def build_stage(stage):
    for j in JOBS[stage]:yield from construct(j,stage)

def tick():
    global BUSY,CURRENT,MESSAGE
    try:
        delay=next(ITER)
        for screen in bpy.data.screens:
            for ar in screen.areas:ar.tag_redraw()
        return delay
    except StopIteration:
        BUSY=False;CURRENT+=1;MESSAGE='Stage complete - inspect, then Next'
        for o in bpy.context.selected_objects:o.select_set(False)
        for screen in bpy.data.screens:
            for ar in screen.areas:ar.tag_redraw()
        return None
    except Exception as e:
        BUSY=False;MESSAGE='ERROR: '+str(e);print(MESSAGE);return None

def view(target=(0,0,.40),distance=1.9,pos=(1.3,-1.7,1.1)):
    for ar in bpy.context.screen.areas:
        if ar.type=='VIEW_3D':
            v=ar.spaces.active;v.region_3d.view_location=target;v.region_3d.view_distance=distance
            v.region_3d.view_rotation=Vector(pos).to_track_quat('Z','Y')
            v.region_3d.view_perspective='ORTHO';v.clip_start=.001;v.clip_end=100
            v.shading.type='SOLID';v.shading.color_type='MATERIAL';v.shading.light='STUDIO'
            v.shading.show_cavity=True;v.shading.cavity_type='BOTH';v.shading.curvature_ridge_factor=1.3
            v.overlay.show_floor=False;v.overlay.show_axis_x=False;v.overlay.show_axis_y=False

class Q4Next(bpy.types.Operator):
    bl_idname='q4.next';bl_label='Next build stage'
    def execute(self,context):
        global ITER,BUSY,MESSAGE
        if BUSY:return {'CANCELLED'}
        if CURRENT>=7:
            finalize();return {'FINISHED'}
        ITER=build_stage(CURRENT);BUSY=True;MESSAGE=NAMES[CURRENT]
        bpy.app.timers.register(tick,first_interval=.5);return {'FINISHED'}

class Q4Inside(bpy.types.Operator):
    bl_idname='q4.inside';bl_label='Internal / cutaway'
    def execute(self,context):
        for o in SHELL:o.hide_set(True)
        view((0,0,.57),1.25,(.8,-1.2,1.6));return {'FINISHED'}

class Q4Outside(bpy.types.Operator):
    bl_idname='q4.outside';bl_label='Full assembly'
    def execute(self,context):
        for o in SHELL:o.hide_set(False)
        view();return {'FINISHED'}

class Q4Drive(bpy.types.Operator):
    bl_idname='q4.drive';bl_label='Inspect FL actuator'
    def execute(self,context):
        view((.30,-.31,.565),.40,(.2,-1,.45));return {'FINISHED'}

class Q4Panel(bpy.types.Panel):
    bl_label='Q4 / LIVE ASSEMBLY';bl_idname='Q4_PT_live'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Q4 Build'
    def draw(self,context):
        l=self.layout;l.label(text='INDUSTRIAL QUADRUPED')
        l.label(text='Visible, incremental modelling')
        l.separator();l.label(text=f'Stage {min(CURRENT+1,8)} / 8 | {COUNT} parts')
        l.label(text=NAMES[min(CURRENT,7)])
        l.label(text=MESSAGE[:38])
        row=l.row();row.enabled=not BUSY;row.operator('q4.next',text='Build next stage' if CURRENT<7 else 'Save completed project',icon='PLAY')
        l.separator();l.operator('q4.outside');l.operator('q4.inside');l.operator('q4.drive')
        l.separator();l.label(text='Timeline = assembly replay')
        l.label(text='Concept / not fabrication drawings')

def finalize():
    global CURRENT,MESSAGE
    CURRENT=8;S.frame_set(FRAME);S.frame_end=FRAME;S.render.fps=24
    view()
    for o in SHELL:o.hide_set(False)
    S['Design note']='12 rotary joints; packaging concept. Gear geometry simplified. No validated torque, thermal, sealing, tolerance or structural calculations.'
    S['Visible build stages']=json.dumps(NAMES)
    notes=bpy.data.texts.get('Q4_DESIGN_NOTES') or bpy.data.texts.new('Q4_DESIGN_NOTES')
    notes.clear();notes.write('Q4 INDUSTRIAL INSPECTION QUADRUPED\n\nBody frame: 800 x 360 mm. Approximate standing height: 760 mm including lidar.\n12 actuators: HAA / HFE / KFE per leg.\nFL hip cutaway: stator, copper coils, rotor, shaft, planetary schematic, output bearing, encoder.\nInterior: 48 illustrative cylindrical cells, BMS, fuse, compute board and heatsink, IMU, restrained branch harness.\nCollections follow build stages. Timeline replays the assembly.\n\nNOT MANUFACTURING READY: cell chemistry/topology, actual gear tooth profiles and ratios, bearing fits, fastener preload, cable bend radii, joint clearances, torque and heat, ingress protection and structural performance require engineering validation. No locomotion controller or dynamic simulation.\n')
    source=bpy.data.texts.get('quadruped_build.py') or bpy.data.texts.new('quadruped_build.py')
    source.clear();source.write(open(os.path.join(ROOT,'quadruped_build.py'),encoding='utf-8').read())
    MESSAGE='Saved: Q4_Industrial_Quadruped.blend'
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Q4_Industrial_Quadruped.blend'))
    with open(os.path.join(ROOT,'Q4_parts.json'),'w',encoding='utf-8') as f:
        json.dump([dict(name=o.name,stage=o['assembly_stage'],material=o.data.materials[0].name,dimensions_m=list(o.dimensions)) for o in OBJS],f,ensure_ascii=False,indent=2)

for cls in [Q4Next,Q4Inside,Q4Outside,Q4Drive,Q4Panel]:bpy.utils.register_class(cls)
def setup_view():
    for ar in bpy.context.screen.areas:
        if ar.type=='CONSOLE':ar.type='VIEW_3D';ar.spaces.active.show_region_ui=True
    view((0,0,.55),1.55,(1,-1.6,1.5))
    return None
bpy.app.timers.register(setup_view,first_interval=.8)
print('Q4 progressive builder ready. Use the Q4 Build sidebar.')
