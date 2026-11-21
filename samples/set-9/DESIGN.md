# NAPLPS pictures · 146–155

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md)

The contact sheet shows the 480 × 460 channel renders in numerical order, five across. The full-size PNGs come directly from the repository renderer at each named size, using the repository stroke font. All twenty images were visually checked at their native sizes. Each stream starts with the full reset, restores the character-set designations, and defines sixteen colour-map entries.

Run `python3 -B validate.py --build` to rebuild the streams, manifest, previews and contact sheet. Run `python3 -B validate.py` to regenerate the streams in memory, compare them with the supplied files, and verify the renders and alternate animation states. Individual generators can also be run directly, for example `python3 -B pages/146-paper-thermal.py`. The generators, encoder and validator use only the Python standard library.

## 146 · Paper Thermal

Four paper colours describe the folds. A light wedge marks the beak, and an orange fold separates the raised neck from the torso. A flattened shadow crosses four projected window panes on the violet floor. Fine highlights mark the exposed paper edges.

## 147 · Soap Film

Eleven nested contour polygons form the interference bands on a stretched film. Each boundary varies in height across a tilted wire frame. Irregular dark patches mark the thinnest film. Narrow bands pool along the lower rail and feed several droplets.

## 148 · Final Spin

Three window bays frame a laundromat after dark. Curved cloth shapes and three open arc marks give the centre drum its sense of rotation. A dedicated palette entry cycles the arc marks between two greens. Interrupted pools of mint and violet stretch out across the pavement below their light sources.

## 149 · Rabbit in the Wall

A deterministic dither softens the spotlight across the plaster wall. The hand enters from the lower left. Knuckle and finger creases make the gesture visible. The silhouette enlarges the raised fingers into ears, with a small arc of lit wall for the eye.

## 150 · Wind Organ

Six terracotta pipes with different bores climb the cliff. Elliptical rims show the angle from which the pipes are seen. The bases share an elongated stone mount, and sampled wind paths approach and leave the six mouths.

## 151 · Kiln Opening

Staggered bricks surround an arch with radial mortar joints. The crosshatched chamber holds a bottle, a jar and a bowl at different depths on the hearth. After an eleven-tenth WAIT, palette updates light the chamber and reveal speckled, burnished and dripped glaze finishes. The opening state is available with `--stage 1`.

## 152 · Pocket Universe

Straight stripes run across the tabletop and supply the pattern refracted into the three glass balls. Horizontal cross-sections reverse the stripe direction and bend their boundaries. Shaded cast shadows, bright edge arcs and small reflected spots place the balls under a common light.

## 153 · Lock Within

Four dotted assembly axes rise from oval seats in a cutaway block. Shaded helical lines form the springs. The bevelled cutaway reveals the curved plug and the pins crossing its seam.

## 154 · Two on the Ice

Each track pairs a lit edge with a shallow blue groove, both sampled along a pair of coupled sine waves. The skaters stand at opposite ends of the ice and face along their tracks.

## 155 · Updraft of Umbrellas

A shared canopy outline is scaled, rotated and foreshortened into six poses. One is inverted. Short wind paths curl around the umbrellas in staggered groups. Open handle arcs carry through all six silhouettes.
