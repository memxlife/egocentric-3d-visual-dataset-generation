# Static Scene Design

## Role In The Dataset

The static scene layer defines the world that camera trajectories move through. A static scene is a
semantically coherent 3D indoor environment with objects, support surfaces, materials, lighting, and
valid camera free space.

One accepted static scene should generate many short egocentric video clips. The scene is therefore
not just a background. It is the persistent hidden state the model should infer from visual change.

## Scene Representation

One static scene is:

```text
z = (layout, structures, support_surfaces, objects, states, materials, lighting, free_space)
```

The scene must include:

- room or local layout;
- support surfaces;
- large furniture or fixtures;
- object instances;
- object categories and instance ids;
- object poses, scale, and support relations;
- material, texture, and color assignments;
- static object states;
- lighting profile;
- valid camera free-space region;
- low-resolution probe views and static-scene acceptance scores.

## Scenario Grammar

Each scenario family must be defined by a grammar, not only an object list.

| Field | Meaning |
|---|---|
| required structures | Furniture, fixtures, or room parts that make the scenario recognizable. |
| required support surfaces | Surfaces where objects may validly rest or attach. |
| required object categories | Categories that must be present for semantic completeness. |
| optional object categories | Plausible categories that increase variety. |
| distractor categories | Plausible extra objects that should not define the scenario. |
| valid co-occurrences | Object combinations that make functional sense. |
| invalid co-occurrences | Category or state combinations that should be rejected. |
| support rules | Which objects may rest, hang, lean, attach, or be contained by which structures. |
| state rules | Static object-state constraints that must be visually meaningful. |
| layout templates | Allowed arrangements of structures and support surfaces. |
| free-space templates | Camera-valid regions and expected viewing distances. |
| lighting templates | Plausible light sources and intensity regimes. |
| material distributions | Category-specific appearance distributions. |
| occlusion requirements | Desired low, medium, and high occlusion regimes. |
| probe-view criteria | Low-resolution tests that decide whether the scene is worth trajectory sampling. |

This grammar prevents plausible-looking category lists from becoming physically or semantically bad
synthetic scenes.

## Scenario Families

Version 1 begins with five scenario families.

| Scenario family | Initial accepted scene target | Why it matters |
|---|---:|---|
| computer desk | 1,000 | Small objects, occlusion, planar surfaces, displays, cables, text-like patterns. |
| kitchen counter | 1,000 | Counter-level scanning, dishware, appliances, reflective materials, structured functional zones. |
| bookshelf/storage shelf | 500 | Repeated structures, vertical organization, partial occlusion, small parallax. |
| living room table/sofa area | 500 | Local objects connected to room-scale context. |
| bathroom vanity | 500 | Mirrors, bottles, sink/counter surfaces, compact free space, specular surfaces. |

## Scenario Cards

### Computer Desk

Required structures:

- desk or table surface;
- nearby wall, chair, window, shelf, lamp, or room context.

Required object categories:

- monitor or laptop;
- input device such as keyboard, mouse, trackpad, or tablet.

Optional and distractor categories:

- mug, phone, notebook, pen, headphones, books, papers, cables, lamp, charger, small electronics,
  boxes, plants, and personal objects.

Layout templates:

- single-monitor desk;
- laptop-centered desk;
- dual-monitor desk;
- L-shaped desk;
- desk against wall;
- desk near window;
- desk with side shelf;
- cluttered student desk;
- minimal office desk.

Accepted examples:

- laptop-centered desk with keyboard, mouse, notebook, mug, and partially visible chair;
- dual-monitor desk with cables, lamp, papers, and shelf context;
- sparse office desk where the required input device and display are visible from several probe
  views.

Rejected examples:

- empty desk with only one object;
- monitor floating above the desk;
- keyboard behind monitor and invisible in all probe views;
- camera free space blocked by chair geometry;
- all objects share the same color and texture;
- a single object occupies more than 80 percent of every probe view.

### Kitchen Counter

Required structures:

- countertop surface;
- at least one functional zone: sink, stove, food-preparation area, or appliance area;
- storage such as cabinet, drawer, shelf, or fridge.

Required object categories:

- dishware, appliance, utensil, bottle, jar, pan, pot, cutting board, towel, food item, or container.

Layout templates:

- straight counter;
- L-shaped counter;
- sink-centered counter;
- stove-centered counter;
- island counter;
- small apartment kitchen;
- dense appliance counter;
- sparse counter.

Accepted examples:

- sink-centered counter with cups, soap bottle, towel, and cabinet context;
- preparation zone with cutting board, knife, bowl, and nearby appliance;
- stove-centered scene with pan, utensils, spice jars, and visible counter edges.

Rejected examples:

- counter exists but no functional zone is visible;
- dishware floats or is embedded in cabinetry;
- sink appears without surrounding counter context;
- objects are placed inside walls or appliances;
- a mirror-like or reflective surface dominates the view without semantic content.

### Bookshelf Or Storage Shelf

Required structures:

- shelf geometry with multiple horizontal or vertical compartments.

Required object categories:

- repeated books, boxes, bins, documents, or storage objects.

Optional and distractor categories:

- plants, photo frames, decorative objects, small devices, toys, and loose papers.

Accepted examples:

- shelf with varied book heights, colors, and thicknesses plus one plant and storage box;
- storage shelf with bins, documents, and small devices at different depths;
- dense shelf with some partial occlusion but multiple object categories visible.

Rejected examples:

- repeated identical books only;
- all books perfectly aligned with no visual variation;
- no nearby distractor objects;
- camera can only see a flat repetitive texture;
- shelf geometry blocks all valid camera viewpoints.

### Living Room Table Or Sofa Area

Required structures:

- sofa, chair, coffee table, side table, TV stand, shelf, rug, or a combination of these.

Required object categories:

- surface or contextual objects such as remote controls, cups, books, plants, toys, bags, pillows,
  blankets, lamps, wall art, curtains, or small decor.

Accepted examples:

- coffee table with remote, books, mug, plant, sofa background, and rug context;
- side table near sofa with lamp, phone, and visible wall/window context;
- TV stand with small objects and partial room-scale context.

Rejected examples:

- large empty room with no local inspection target;
- sofa fills the view and no small object is visible;
- table floats above rug or intersects sofa;
- visual content is only blank wall or floor.

### Bathroom Vanity

Required structures:

- sink and counter;
- mirror or reflective surface;
- cabinet, shelf, towel rack, or drawer.

Required object categories:

- bottles, toothbrushes, soap, towels, cosmetics, cups, tissue boxes, or containers.

Accepted examples:

- vanity with sink, mirror, toothbrush cup, soap bottle, towel, and cabinet context;
- cluttered counter with cosmetics and bottles, where mirror does not dominate all probe views;
- compact bathroom view with visible sink/counter geometry and valid camera free space.

Rejected examples:

- mirror dominates all views;
- sink and vanity are visible but no small objects are present;
- bottles are placed inside the sink in implausible ways;
- specular surfaces produce degenerate segmentation or depth artifacts;
- toothbrush appears far from cup, holder, sink, or medicine cabinet.

## Support And Placement Constraints

Support relations are part of the scene grammar. They should be explicit in metadata and checked
before trajectory generation.

Examples:

- keyboard must be on a desk surface or tray;
- mouse must be near keyboard or trackpad area;
- monitor must be on desk, monitor arm, wall mount, or plausible stand;
- mug must rest on a horizontal support surface unless it is in a physically plausible fallen state;
- books may lie flat, stack, or stand against support;
- cables may lie on desk, hang over edge, or connect devices;
- toothbrush should appear near cup, holder, sink, medicine cabinet, or vanity area;
- towel-hanging state requires hook, rack, cabinet handle, or other vertical support;
- sink objects must appear near sink or vanity/counter surface.

Reject severe interpenetration, floating objects, impossible support relations, implausible scale,
and object placements that violate the scenario grammar.

## Static Object-State Constraints

Object states must be visually meaningful, not metadata decorations.

| State | Required visual constraint |
|---|---|
| laptop open | Visible hinge angle and distinct keyboard/screen planes. |
| laptop closed | Single closed slab on valid support surface. |
| monitor on | Static screen content or plausible emissive display. |
| monitor off | Glossy or dark screen surface with no changing content. |
| cabinet or drawer open | Visible opening, interior geometry, or dark interior region. |
| fallen cup | Physically plausible support contact and no table intersection. |
| towel hanging | Vertical support, hook, rack, or edge contact. |
| mirror present | Planar reflective material bounded by frame or wall; probe views must not be dominated by mirror artifacts. |

The world remains static during a clip. State variation occurs across scenes, not during a sequence.

## Material, Texture, And Color Distributions

Appearance variation should be controlled by category.

| Category | Plausible material distribution |
|---|---|
| desk surface | Wood, laminate, painted metal, glass. |
| keyboard | Matte plastic, dark or light keycaps, slight roughness. |
| monitor screen | Glossy black/off, emissive/on, reflective surface. |
| mug | Ceramic, matte or glossy, colored or patterned. |
| countertop | Stone, laminate, wood, stainless steel. |
| bottle | Transparent plastic, translucent plastic, opaque ceramic, metal. |
| mirror | High reflectance, planar, framed or wall-bounded. |
| books | Paper pages, colored covers, text-like patterns. |
| towel | Soft fabric, folded or hanging, non-metallic rough material. |

Avoid arbitrary random color assignment that breaks semantic plausibility. Also avoid no variation,
where all objects share the same material, color, and texture family.

## Clutter And Occlusion

Each scene samples a clutter level:

```text
sparse | medium | dense
```

Initial object count ranges:

| Scenario | Sparse | Medium | Dense |
|---|---:|---:|---:|
| desk | 4-8 | 8-16 | 16-32 |
| kitchen counter | 5-10 | 10-24 | 24-48 |
| bookshelf/storage | 10-30 | 30-80 | 80-160 |
| living room table/sofa | 5-12 | 12-28 | 28-56 |
| bathroom vanity | 4-8 | 8-18 | 18-36 |

Object count is only a proxy. Probe-view metrics must also measure visible object count,
foreground pixel ratio, object area distribution, occlusion ratio, number of partially visible
objects, semantic entropy, instance entropy, small-object pixel mass, and dominant-object area.

## Static Scene Acceptance

A static scene is accepted only if it passes:

```text
C_scene(z) =
  C_semantic_complete
  and C_physical
  and C_probe_visual_content
  and C_free_space
  and C_appearance_diverse
```

These checks happen before expensive trajectory rendering. A scene with valid geometry but no useful
probe viewpoints is rejected because it cannot produce meaningful egocentric visual scanning data.
