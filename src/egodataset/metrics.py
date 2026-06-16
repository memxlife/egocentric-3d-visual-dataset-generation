from __future__ import annotations

import math
from collections import Counter
from typing import Any

from egodataset.schema import Episode


def compute_episode_metrics(episode: Episode, scenario: dict[str, Any] | None) -> dict[str, dict]:
    if not scenario:
        return {
            "generation_speed": _metric(True, 1.0, [], {"reason": "no scenario card"}),
            "realism": _metric(True, 1.0, [], {"reason": "no scenario card"}),
            "per_scenario_comprehensiveness": _metric(True, 1.0, [], {"reason": "no scenario card"}),
            "cross_scenario_diversity": _metric(True, 1.0, [], {"reason": "no scenario card"}),
        }

    return {
        "generation_speed": _generation_speed_metric(episode, scenario),
        "realism": _realism_metric(episode, scenario),
        "per_scenario_comprehensiveness": _scenario_coverage_metric(episode, scenario),
        "cross_scenario_diversity": _diversity_metric(episode, scenario),
    }


def _generation_speed_metric(episode: Episode, scenario: dict[str, Any]) -> dict:
    timing = episode.diagnostics.get("timing", {})
    fps = float(timing.get("raw_frames_per_second", 0.0))
    minimum_fps = float(scenario.get("speed", {}).get("min_raw_frames_per_second", 0.0))
    failures = []
    if fps < minimum_fps:
        failures.append(f"raw_fps {fps:.2f} < {minimum_fps:.2f}")
    score = 1.0 if minimum_fps <= 0 else min(fps / minimum_fps, 1.0)
    return _metric(not failures, score, failures, {"raw_frames_per_second": fps})


def _realism_metric(episode: Episode, scenario: dict[str, Any]) -> dict:
    rules = scenario.get("realism", {})
    required_groups = rules.get("required_object_groups", [])
    visible_categories = set(episode.diagnostics.get("visible_object_categories", []))
    failures = []
    passed_groups = 0

    for group in required_groups:
        any_of = set(group.get("any_of", []))
        group_name = group.get("name", ",".join(sorted(any_of)))
        if visible_categories & any_of:
            passed_groups += 1
        else:
            failures.append(f"missing_required_object_group:{group_name}")

    hard_checks = rules.get("hard_checks", [])
    assumed_passed = [check for check in hard_checks if check.get("mock_assume_passed", False)]
    for check in hard_checks:
        if check not in assumed_passed:
            failures.append(f"insufficient_evidence:{check.get('name', 'unnamed_check')}")

    group_score = 1.0 if not required_groups else passed_groups / len(required_groups)
    check_score = 1.0 if not hard_checks else len(assumed_passed) / len(hard_checks)
    score = (group_score + check_score) / 2.0
    threshold = float(rules.get("min_score", 0.0))
    if score < threshold:
        failures.append(f"realism_score {score:.2f} < {threshold:.2f}")
    return _metric(not failures, score, failures, {"visible_categories": sorted(visible_categories)})


def _scenario_coverage_metric(episode: Episode, scenario: dict[str, Any]) -> dict:
    coverage = scenario.get("coverage", {})
    action_result = _required_action_coverage(episode, coverage.get("required_actions", []))
    viewpoint_result = _viewpoint_bin_coverage(episode, coverage.get("viewpoint_bins", {}))
    visibility_result = _visibility_event_coverage(
        episode, coverage.get("required_visibility_events", {})
    )
    object_result = _required_object_coverage(episode, scenario.get("realism", {}))
    weights = coverage.get("weights", {})
    score = (
        float(weights.get("view", 0.35)) * viewpoint_result["score"]
        + float(weights.get("motion", 0.25)) * action_result["score"]
        + float(weights.get("visibility", 0.25)) * visibility_result["score"]
        + float(weights.get("object", 0.15)) * object_result["score"]
    )
    threshold = float(coverage.get("min_score", 0.0))
    failures = []
    for result in [action_result, viewpoint_result, visibility_result, object_result]:
        failures.extend(result["failures"])
    if score < threshold:
        failures.append(f"scenario_coverage_score {score:.2f} < {threshold:.2f}")
    return _metric(
        not failures,
        score,
        failures,
        {
            "action_coverage": action_result,
            "viewpoint_coverage": viewpoint_result,
            "visibility_coverage": visibility_result,
            "object_coverage": object_result,
        },
    )


def _diversity_metric(episode: Episode, scenario: dict[str, Any]) -> dict:
    diversity = scenario.get("diversity", {})
    required_axes = diversity.get("required_episode_axes", [])
    evidence = {
        "scenario_card_id": scenario.get("id"),
        "policy": episode.policy,
        "visible_categories": episode.diagnostics.get("visible_object_categories", []),
        "trajectory_length": len(episode.frames),
    }
    failures = []
    for axis in required_axes:
        value = evidence.get(axis)
        if value in (None, [], ""):
            failures.append(f"missing_diversity_axis:{axis}")
    score = 1.0 if not required_axes else (len(required_axes) - len(failures)) / len(required_axes)
    threshold = float(diversity.get("min_episode_score", 0.0))
    if score < threshold:
        failures.append(f"diversity_score {score:.2f} < {threshold:.2f}")
    return _metric(not failures, score, failures, evidence)


def _required_action_coverage(episode: Episode, required_actions: list[str]) -> dict:
    actions = [frame.action for frame in episode.frames]
    action_counts = Counter(actions)
    missing = [action for action in required_actions if action_counts[action] == 0]
    score = 1.0 if not required_actions else (len(required_actions) - len(missing)) / len(required_actions)
    failures = [f"missing_required_action:{action}" for action in missing]
    return {"score": score, "failures": failures, "action_counts": dict(action_counts)}


def _viewpoint_bin_coverage(episode: Episode, bin_config: dict[str, Any]) -> dict:
    if not bin_config:
        return {"score": 1.0, "failures": [], "visited_bins": []}

    visited = set()
    for frame in episode.frames:
        pose = frame.pose
        bin_key = []
        for name, spec in bin_config.items():
            if name.startswith("_"):
                continue
            value = float(pose[_pose_key(name)])
            bin_key.append(f"{name}:{_bin_label(value, spec)}")
        visited.add("|".join(bin_key))

    min_bins = int(bin_config.get("_min_unique_bins", 0))
    visited_count = len(visited)
    score = 1.0 if min_bins <= 0 else min(visited_count / min_bins, 1.0)
    failures = []
    if visited_count < min_bins:
        failures.append(f"viewpoint_bins {visited_count} < {min_bins}")
    return {"score": score, "failures": failures, "visited_bins": sorted(visited)}


def _visibility_event_coverage(episode: Episode, event_config: dict[str, Any]) -> dict:
    if not event_config.get("require_disappear_reappear", False):
        return {"score": 1.0, "failures": [], "events": []}

    timelines: dict[str, list[bool]] = {}
    for frame in episode.frames:
        visible = {str(obj["instance_id"]) for obj in frame.visible_objects}
        for instance_id in visible:
            timelines.setdefault(instance_id, [])
        for instance_id in timelines:
            timelines[instance_id].append(instance_id in visible)

    events = []
    for instance_id, timeline in timelines.items():
        seen = False
        hidden_after_seen = False
        for value in timeline:
            if value and hidden_after_seen:
                events.append(instance_id)
                break
            if value:
                seen = True
            elif seen:
                hidden_after_seen = True

    score = 1.0 if events else 0.0
    failures = [] if events else ["no_disappear_reappear_event"]
    return {"score": score, "failures": failures, "events": events}


def _required_object_coverage(episode: Episode, realism: dict[str, Any]) -> dict:
    groups = realism.get("required_object_groups", [])
    visible_categories = set(episode.diagnostics.get("visible_object_categories", []))
    missing = []
    for group in groups:
        any_of = set(group.get("any_of", []))
        if not (visible_categories & any_of):
            missing.append(group.get("name", ",".join(sorted(any_of))))
    score = 1.0 if not groups else (len(groups) - len(missing)) / len(groups)
    return {
        "score": score,
        "failures": [f"missing_required_object_group:{name}" for name in missing],
    }


def _pose_key(name: str) -> str:
    aliases = {"horizontal": "x", "height": "y", "distance": "z"}
    return aliases.get(name, name)


def _bin_label(value: float, spec: Any) -> str:
    if isinstance(spec, dict) and "edges" in spec:
        edges = [float(edge) for edge in spec["edges"]]
        labels = spec.get("labels", [])
        index = sum(value >= edge for edge in edges)
        if labels and index < len(labels):
            return str(labels[index])
        return str(index)
    if isinstance(spec, dict) and "width" in spec:
        width = float(spec["width"])
        return str(math.floor(value / width))
    return "all"


def _metric(passed: bool, score: float, failures: list[str], evidence: dict[str, Any]) -> dict:
    return {
        "passed": passed,
        "score": round(float(score), 6),
        "failures": failures,
        "evidence": evidence,
    }
