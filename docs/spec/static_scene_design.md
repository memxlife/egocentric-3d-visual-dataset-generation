# Static Scene Design

## Role In The Dataset

The static scene layer defines the world that camera trajectories move through. A static scene is a
semantically coherent 3D indoor environment with objects, support surfaces, materials, lighting, and
valid camera free space.

One accepted static scene should generate many short egocentric video clips.

## Scene Representation

One static scene is:

```text
z = (layout, objects, geometry, materials, appearance, semantics, free_space)
```

The scene must include:

- room or local layout;
- support surfaces;
- large furniture or fixtures;
- object instances;
- object categories and instance ids;
- object poses, scale, and support relations;
- material, texture, and color assignments;
- lighting profile;
- valid camera free-space region.

## Scenario Families

Version 1 begins with five scenario families.

| Scenario family | Initial accepted scene target | Why it matters |
|---|---:|---|
| computer desk | 1,000 | Small objects, occlusion, planar surfaces, displays, cables, text-like patterns. |
| kitchen counter | 1,000 | Counter-level scanning, dishware, appliances, reflective materials, structured functional zones. |
| bookshelf/storage shelf | 500 | Repeated structures, vertical organization, partial occlusion, small parallax. |
| living room table/sofa area | 500 | Local objects connected to room-scale context. |
| bathroom vanity | 500 | Mirrors, bottles, sink/counter surfaces, compact free space, specular surfaces. |

Total initial target:

```text
3,500 accepted static scenes
```

## Computer Desk Requirements

Required content:

- desk or table surface;
- monitor or laptop;
- input device such as keyboard, mouse, trackpad, or tablet;
- personal or clutter objects such as mug, phone, notebook, pen, headphones, books, papers, cables,
  lamp, charger, small electronics, or boxes;
- background context such as wall, chair, shelf, window, or lamp.

Layout variants:

- single-monitor center desk;
- laptop-centered desk;
- dual-monitor desk;
- L-shaped desk;
- desk against wall;
- desk near window;
- desk with side shelf;
- cluttered student desk;
- minimal office desk.

## Kitchen Counter Requirements

Required content:

- countertop surface;
- at least one functional zone: sink, stove, food-preparation area, or appliance area;
- storage structures such as cabinet, drawer, shelf, or fridge;
- dishware or appliance objects;
- optional food, tools, towels, bottles, jars, pans, pots, cutting boards, utensils, and small
  appliances.

Layout variants:

- straight counter;
- L-shaped counter;
- sink-centered counter;
- stove-centered counter;
- island counter;
- small apartment kitchen;
- dense appliance counter;
- sparse counter.

## Bookshelf Or Storage Shelf Requirements

Required content:

- shelf structure;
- repeated books or storage objects;
- boxes, bins, decorative objects, plants, photo frames, small devices, or documents.

The scene may contain many repeated objects, but should vary size, color, thickness, orientation,
and nearby distractors.

## Living Room Table Or Sofa-Area Requirements

Required content:

- sofa, chair, coffee table, side table, TV stand, shelf, or rug;
- surface objects such as remote controls, cups, books, plants, toys, bags, pillows, blankets, and
  decorative items;
- background structures such as windows, doors, wall art, lamps, or curtains.

## Bathroom Vanity Requirements

Required content:

- sink and counter;
- mirror or reflective surface;
- cabinet, shelf, towel rack, or drawer;
- bottles, toothbrushes, soap, towels, cosmetics, cups, tissue boxes, or containers.

## Object Density

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

Other scenario families should be calibrated during pilot generation.

## Variation Axes

Each scenario family must vary:

- layout template;
- object category set;
- object count;
- object instance identity;
- object geometry and shape family;
- object size;
- object pose;
- support relation;
- material;
- texture;
- color;
- roughness, metallicity, transparency, and reflectance;
- static state;
- lighting;
- free-space geometry.

## Static Object States

Objects may have static states that do not change during a clip:

- laptop open or closed;
- book open or closed;
- drawer or cabinet open or closed;
- cup upright or physically plausible fallen;
- chair pulled in or out;
- towel folded or hanging;
- sink empty or containing dishes;
- monitor on, off, or displaying static content.

## Static Scene Acceptance

A static scene is accepted only if it passes:

- semantic completeness;
- physical plausibility;
- visual richness from probe views;
- free-space availability;
- appearance diversity.

These checks happen before expensive trajectory rendering.
