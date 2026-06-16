# Splits And Generalization

## Design Goal

The dataset should support controlled generalization claims. A random frame split is not enough
because frames from the same clip, starts from the same scene, and scenes from the same layout
template are strongly correlated.

## Split Files

Version 1 should provide:

```text
splits/
  train.txt
  val_seen_category.txt
  test_scene_held_out.txt
  test_object_category_held_out.txt
  test_object_instance_held_out.txt
  test_layout_held_out.txt
  test_trajectory_held_out.txt
  test_material_held_out.txt
  test_cross_scenario.txt
```

Each line should identify an episode id unless the split explicitly operates at scene level. The
split manifest must state whether it lists scenes, episodes, or both.

## Split Policies

| Split | Held out | Claim it tests |
|---|---|---|
| `val_seen_category` | Episodes from seen scenes/categories but unseen seeds. | Basic interpolation and training stability. |
| `test_scene_held_out` | Entire static scenes. | Generalization to new layouts and object arrangements within known scenario families. |
| `test_object_category_held_out` | Selected object categories. | Ability to handle unseen semantic categories when possible. |
| `test_object_instance_held_out` | Specific meshes/assets. | Generalization beyond memorized object geometry. |
| `test_layout_held_out` | Layout templates. | Generalization to new spatial arrangements. |
| `test_trajectory_held_out` | Motion primitives or primitive compositions. | Generalization to new camera motion patterns. |
| `test_material_held_out` | Material or texture families. | Appearance generalization. |
| `test_cross_scenario` | Entire scenario family when feasible. | Transfer across functional scene types. |

## Leakage Rules

The split builder must prevent:

- frames from the same clip appearing in both train and test;
- clips from the same start viewpoint crossing train/test unless explicitly testing trajectory
  variation from the same start;
- episodes from the same static scene crossing a scene-held-out split;
- object instances or meshes crossing an instance-held-out split;
- layout templates crossing a layout-held-out split.

## Metadata Requirements

Each split must record:

- split name;
- split version;
- construction date;
- generator commit;
- dataset version;
- selection rules;
- excluded scene ids;
- excluded object categories or instances;
- excluded layout templates;
- excluded trajectory primitives;
- counts by scenario family, scene, primitive, and anchor category.

## Failure Modes Prevented

The split policy prevents overly optimistic evaluation caused by correlated frames, repeated
scenes, repeated object meshes, repeated layouts, or repeated trajectory primitives. It also makes
clear which generalization claim each test set can and cannot support.
