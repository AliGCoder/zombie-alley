# Blender script: models loose, hanging clothes for the zombie (models/zombie.glb) and exports models/zombie_clothes.glb
#   blender --background --factory-startup --python tools/make_clothes.py
# Clothes are built from the body surface, then loosened: the shirt falls straight from the chest and flares,
# sleeves are baggy, trousers hang wide from the thigh, hems overhang, and vertical drape folds are added.
# Each garment keeps the body's bone weights, so it moves with the zombie skeleton in the game.
import bpy, bmesh, math, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "models", "zombie.glb"))

# mesh-local space here is centimetres: height = -y, front = -z (becomes z up, -y front again after export)
H = lambda co: -co.y
F = lambda co: co.z
mesh_by_mat = {o.data.materials[0].name: o for o in bpy.data.objects if o.type == 'MESH' and o.data.materials}
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')


def dup_join(name, mats):
    objs = []
    for m in mats:
        s = mesh_by_mat[m]; c = s.copy(); c.data = s.data.copy(); c.name = name
        s.users_collection[0].objects.link(c); objs.append(c)
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
        bpy.ops.object.join()
    o = objs[0]; o.name = name; o.data.name = name
    return o


def cyl(co, cx, cz):   # polar coords around a vertical axis
    dx, dz = co.x - cx, co.z - cz
    return math.hypot(dx, dz), math.atan2(dz, dx)


def keep_region(bm, keep):
    gone = [f for f in bm.faces if not all(keep(v.co) for v in f.verts)]
    bmesh.ops.delete(bm, geom=gone, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')


def boundary(bm, test):
    return [e for e in bm.edges if e.is_boundary and all(test(v.co) for v in e.verts)]


def extrude_hem(bm, edges, move):
    if not edges: return
    r = bmesh.ops.extrude_edge_only(bm, edges=edges)
    for v in [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]: move(v.co)


def smooth(bm, n=3, f=0.35):
    inner = [v for v in bm.verts if not v.is_boundary]
    for _ in range(n):
        bmesh.ops.smooth_vert(bm, verts=inner, factor=f, use_axis_x=True, use_axis_y=True, use_axis_z=True)


# ---------------------------------------------------------------- shirt
def make_shirt(name, sleeve):
    o = dup_join(name, ['Std_Skin_Body', 'Std_Skin_Arm'])
    bm = bmesh.new(); bm.from_mesh(o.data)

    def keep(co):
        h, x = H(co), abs(co.x)
        top = (149.0 - (5.0 if F(co) < -2 else 0.0)) if x < 11 else 175.0
        return 96.0 <= h <= top and x <= sleeve
    keep_region(bm, keep)
    torso = [v for v in bm.verts if abs(v.co.x) < 19]
    cz = sum(v.co.z for v in torso) / len(torso)
    # chest profile: widest radius per angle around the ribcage
    bins = 36; R = [0.0] * bins
    for v in torso:
        if 124 <= H(v.co) <= 140:
            r, a = cyl(v.co, 0, cz); i = int((a + math.pi) / (2 * math.pi) * bins) % bins; R[i] = max(R[i], r)
    for i in range(bins):
        if R[i] == 0: R[i] = max(R)
    Rs = [(R[i - 1] + 2 * R[i] + R[(i + 1) % bins]) / 4 for i in range(bins)]
    # sleeve axis: centre of the arm cross-section every 2cm along x
    sl = {}
    for v in bm.verts:
        if abs(v.co.x) >= 15:
            k = (1 if v.co.x > 0 else -1, int(abs(v.co.x) // 2)); sl.setdefault(k, []).append(v.co.copy())
    axis = {k: (sum(c.y for c in cs) / len(cs), sum(c.z for c in cs) / len(cs)) for k, cs in sl.items()}

    def sleeve_axis(co):
        return axis.get((1 if co.x > 0 else -1, int(abs(co.x) // 2)), (co.y, co.z))
    for v in bm.verts:
        co, h, x = v.co, H(v.co), abs(v.co.x)
        # torso: hangs straight down from the chest, flaring a little toward the hem, with drape folds
        r, a = cyl(co, 0, cz)
        i = int((a + math.pi) / (2 * math.pi) * bins) % bins
        hang = max(0.0, min(1.0, (136 - h) / 30))
        rt = max(r + 1.6, Rs[i] * (1.0 + 0.06 * hang) + 0.8) if h < 136 else r + 1.6
        rt += hang * 0.7 * math.sin(a * 7 + h * 0.08)
        tx, tz = rt * math.cos(a), cz + rt * math.sin(a)
        # sleeve: baggy around the arm's own axis
        ay, az = sleeve_axis(co)
        dy, dz = co.y - ay, co.z - az; rr = math.hypot(dy, dz) or 1
        s = (rr * 1.3 + 1.3) / rr
        sy, sz = ay + dy * s, az + dz * s
        w = max(0.0, min(1.0, (x - 16) / 7))       # blend torso -> sleeve over the shoulder
        nx = co.x if x >= 19 else co.x * w + tx * (1 - w)
        co.x, co.y, co.z = nx, sy * w + co.y * (1 - w), sz * w + tz * (1 - w)
    smooth(bm)

    # hems: the shirt hangs 7cm below the waist and flares; sleeve ends overhang the arm
    def hem(co):
        r, a = cyl(co, 0, cz); r *= 1.05
        co.x, co.z, co.y = r * math.cos(a), cz + r * math.sin(a), co.y + 7.0
    extrude_hem(bm, boundary(bm, lambda c: H(c) < 103 and abs(c.x) < 22), hem)

    def cuff(co):
        ay, az = sleeve_axis(co)
        co.y = ay + (co.y - ay) * 1.12; co.z = az + (co.z - az) * 1.12; co.x += 2.5 if co.x > 0 else -2.5
    extrude_hem(bm, boundary(bm, lambda c: abs(c.x) > sleeve - 6), cuff)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free()
    return o


# ---------------------------------------------------------------- trousers
def make_trousers(name):
    o = dup_join(name, ['Std_Skin_Leg', 'Std_Skin_Body'])
    bm = bmesh.new(); bm.from_mesh(o.data)
    keep_region(bm, lambda co: 7.5 <= H(co) <= 101 and abs(co.x) <= 24)
    pel = [v for v in bm.verts if H(v.co) > 85]
    cz = sum(v.co.z for v in pel) / len(pel)
    # leg axes every 3cm of height, and thigh radius per leg
    sl = {}
    for v in bm.verts:
        if H(v.co) < 86:
            k = (1 if v.co.x > 0 else -1, int(H(v.co) // 3)); sl.setdefault(k, []).append(v.co.copy())
    axis = {k: (sum(c.x for c in cs) / len(cs), sum(c.z for c in cs) / len(cs)) for k, cs in sl.items()}
    thigh = {}
    for v in bm.verts:
        h = H(v.co)
        if 68 <= h <= 78:
            sd = 1 if v.co.x > 0 else -1; ax, az = axis[(sd, int(h // 3))]
            thigh[sd] = max(thigh.get(sd, 0), math.hypot(v.co.x - ax, v.co.z - az))
    for v in bm.verts:
        co, h = v.co, H(v.co); sd = 1 if co.x > 0 else -1
        # pelvis / seat: a little roomier than the body
        r, a = cyl(co, 0, cz); px, pz = (r + 1.8) * math.cos(a), cz + (r + 1.8) * math.sin(a)
        # legs: hang wide and straight from the thigh, with drape folds
        ax, az = axis.get((sd, int(h // 3)), (co.x, co.z))
        dx, dz = co.x - ax, co.z - az; rl = math.hypot(dx, dz) or 1; al = math.atan2(dz, dx)
        t = max(0.0, min(1.0, (70 - h) / 62))
        tl = max(rl + 1.5, thigh.get(sd, rl) * (0.88 - 0.12 * t)) + t * 0.6 * math.sin(al * 6 + h * 0.1)
        lx, lz = ax + tl * math.cos(al), az + tl * math.sin(al)
        w = max(0.0, min(1.0, (84 - h) / 8))       # blend seat -> legs
        co.x, co.z = lx * w + px * (1 - w), lz * w + pz * (1 - w)
    smooth(bm)

    def pool(co):   # trouser bottoms pool over the shoes
        sd = 1 if co.x > 0 else -1; ax, az = axis.get((sd, 3), (co.x, co.z))
        co.x = ax + (co.x - ax) * 1.1; co.z = az + (co.z - az) * 1.1; co.y += 3.0
    extrude_hem(bm, boundary(bm, lambda c: H(c) < 12), pool)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free()
    return o


clothes = [make_shirt('Shirt_Long', 66.0), make_shirt('Shirt_Short', 38.0), make_trousers('Trousers')]
for c in clothes:
    mat = bpy.data.materials.new('Cloth_' + c.name); mat.use_backface_culling = False
    c.data.materials.clear(); c.data.materials.append(mat)
    for p in c.data.polygons: p.use_smooth = True
    c.modifiers.clear(); md = c.modifiers.new('Armature', 'ARMATURE'); md.object = arm
    print('CLOTH', c.name, len(c.data.vertices), 'verts')

# export just the clothes and the skeleton
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o not in clothes: bpy.data.objects.remove(o)
bpy.ops.object.select_all(action='DESELECT')
for o in clothes + [arm]: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT, "models", "zombie_clothes.glb"), export_format='GLB',
                          use_selection=True, export_animations=False, export_morph=False, export_skins=True)
print('EXPORTED')
