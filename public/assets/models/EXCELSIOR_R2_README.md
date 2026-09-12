# EXCELSIOR R2 — ARK SHIP form study

Reference-based Blender revision, 2026-09-12. Geometry only, no image textures or background objects in the exported ship scene.

- `EXCELSIOR_R2.blend`: editable scene and embedded builder scripts; the earlier scene remains preserved.
- `EXCELSIOR_R2.glb`: active ship scene for web viewing, 836 meshes and four neutral clay materials.
- `../images/EXCELSIOR_R2_hero.png`: perspective exterior, transparent background.
- `../images/EXCELSIOR_R2_interior.png`: outer panels and upper deck surfaces hidden for inspection.
- `../images/EXCELSIOR_R2_top.png`, `side.png`, `front.png`: orthographic inspections (each filename has the `EXCELSIOR_R2_` prefix).

Measured geometry envelope: 312.0 × 195.9 × 83.0 meters. The source orthographic sheet labels 312 × 198 × 82 meters.

The four swept habitat shells contain three deck surfaces, transverse frames, equipment units, conduits and exposed side trusses. Other assemblies include the pressure spine, flared command module, sensor boom, annular hub, paired support spars, cargo cassettes, engine containment frame and five hollow nozzle meshes. End frames, service hatches, fasteners and manifold fittings are geometry.

The supplied concept images differ between views. This revision approximates their curved silhouette and overall proportions; it is not an exact reconstruction. Interior systems are visual design interpretations, not validated spacecraft engineering.

Collections organize the main assemblies. The custom EXCELSIOR controls are available in the current Blender session; on reopening, the model remains editable through the standard Outliner. Embedded scripts are not automatically executed.
