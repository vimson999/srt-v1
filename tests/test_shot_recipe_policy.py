import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
RECIPES_PATH = ROOT / "templates" / "shot-recipe.json"
REGISTRY_PATH = ROOT / "templates" / "shot-language.yaml"

REQUIRED_LANGUAGE_FAMILIES = {
    "report_reveal",
    "sequential_card_build",
    "aligned_comparison",
    "causal_flow",
    "data_hero",
    "conclusion_resolve",
    "pause_hold",
    "clean_cut",
}
LIFECYCLE_FIELDS = ("entry", "development", "information_peak", "reading_hold", "exit")
FORBIDDEN_RENDERER_KEYS = {
    "renderer",
    "renderer_name",
    "remotion_component",
    "hyperframes_component",
    "after_effects_template",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing required artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), f"{path.name} root must be an object"
    return value


def registry_actions() -> dict[str, set[str]]:
    registry = load_json(REGISTRY_PATH)
    return {
        family["id"]: set(family["visual_actions"])
        for family in registry["families"]
    }


def iter_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_keys(child)


def validate_recipe(recipe: Any, language_actions: dict[str, set[str]]) -> list[str]:
    if not isinstance(recipe, dict):
        return ["recipe must be an object"]

    recipe_id = recipe.get("id", "<missing>")
    errors: list[str] = []
    for field in ("id", "shot_language", "fit", "avoid", "motion_personality", "pitfalls"):
        value = recipe.get(field)
        if field in {"fit", "avoid", "pitfalls"}:
            if not isinstance(value, list) or not value:
                errors.append(f"{recipe_id}: {field} must be a non-empty array")
        elif not isinstance(value, str) or not value.strip():
            errors.append(f"{recipe_id}: {field} must be non-empty text")

    actions = recipe.get("visual_actions")
    if not isinstance(actions, list) or not actions:
        errors.append(f"{recipe_id}: visual_actions must be a non-empty array")

    for field in LIFECYCLE_FIELDS:
        value = recipe.get(field)
        if not isinstance(value, dict) or not value:
            errors.append(f"{recipe_id}: {field} must be a non-empty object")

    motion_budget = recipe.get("motion_budget")
    if not isinstance(motion_budget, dict):
        errors.append(f"{recipe_id}: motion_budget must be an object")
    elif not isinstance(motion_budget.get("primary_responsibility"), str):
        errors.append(f"{recipe_id}: motion_budget needs primary_responsibility")

    duration = recipe.get("duration_guidance")
    if not isinstance(duration, dict):
        errors.append(f"{recipe_id}: duration_guidance must be an object")
    else:
        if duration.get("fixed_seconds") is not False:
            errors.append(f"{recipe_id}: duration_guidance must not fix seconds")
        if not isinstance(duration.get("derive_from"), list) or not duration["derive_from"]:
            errors.append(f"{recipe_id}: duration_guidance needs derive_from")

    implementation = recipe.get("reference_implementation")
    if not isinstance(implementation, dict):
        errors.append(f"{recipe_id}: reference_implementation must be an object")
    else:
        if implementation.get("kind") != "state_timeline":
            errors.append(f"{recipe_id}: reference_implementation.kind must be state_timeline")
        steps = implementation.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{recipe_id}: reference_implementation.steps must be non-empty")
        else:
            phases = [step.get("phase") for step in steps if isinstance(step, dict)]
            if phases != ["entry", "development", "peak", "hold", "exit"]:
                errors.append(f"{recipe_id}: reference implementation must cover lifecycle order")
        adapter_contract = implementation.get("adapter_contract")
        if not isinstance(adapter_contract, list) or not adapter_contract:
            errors.append(f"{recipe_id}: reference implementation needs adapter_contract")

    family = recipe.get("shot_language")
    if family not in language_actions:
        errors.append(f"{recipe_id}: unknown shot_language {family}")
    elif isinstance(actions, list) and not set(actions) <= language_actions[family]:
        errors.append(f"{recipe_id}: visual_actions are incompatible with {family}")

    if recipe.get("renderer_neutral") is not True:
        errors.append(f"{recipe_id}: recipe must be renderer-neutral")
    if FORBIDDEN_RENDERER_KEYS.intersection(iter_keys(recipe)):
        errors.append(f"{recipe_id}: recipe hard-codes a renderer")

    return errors


def test_recipe_set_covers_the_first_useful_language_families():
    document = load_json(RECIPES_PATH)
    assert document["schema_version"] == 1
    recipes = document["recipes"]
    assert isinstance(recipes, list) and recipes
    covered = {recipe["shot_language"] for recipe in recipes}
    assert REQUIRED_LANGUAGE_FAMILIES <= covered


def test_recipe_set_defines_an_explainable_shot_record_selection():
    contract = load_json(RECIPES_PATH)["shot_record_contract"]
    assert contract["field"] == "shot_recipe"
    assert contract["id_field"] == "id"
    assert contract["reason_field"] == "selection_reason"
    assert contract["require_reason"] is True
    assert contract["gap_field"] == "recipe_gap"
    assert contract["require_gap_when_unselected"] is True


def test_every_recipe_passes_the_renderer_neutral_contract():
    document = load_json(RECIPES_PATH)
    actions = registry_actions()
    ids = [recipe["id"] for recipe in document["recipes"]]
    assert len(ids) == len(set(ids)), "recipe ids must be unique"
    for recipe in document["recipes"]:
        assert validate_recipe(recipe, actions) == []


def test_missing_lifecycle_phase_is_rejected():
    document = load_json(RECIPES_PATH)
    recipe = copy.deepcopy(document["recipes"][0])
    recipe.pop("development")
    errors = validate_recipe(recipe, registry_actions())
    assert any("development" in error for error in errors)


def test_missing_reference_implementation_is_rejected():
    document = load_json(RECIPES_PATH)
    recipe = copy.deepcopy(document["recipes"][0])
    recipe.pop("reference_implementation")
    errors = validate_recipe(recipe, registry_actions())
    assert any("reference_implementation" in error for error in errors)


def test_renderer_specific_recipe_is_rejected():
    document = load_json(RECIPES_PATH)
    recipe = copy.deepcopy(document["recipes"][0])
    recipe["renderer_name"] = "specific-engine"
    errors = validate_recipe(recipe, registry_actions())
    assert any("hard-codes a renderer" in error for error in errors)


def test_nested_renderer_specific_recipe_is_rejected():
    document = load_json(RECIPES_PATH)
    recipe = copy.deepcopy(document["recipes"][0])
    recipe["reference_implementation"]["remotion_component"] = "EvidenceShot"
    errors = validate_recipe(recipe, registry_actions())
    assert any("hard-codes a renderer" in error for error in errors)


def run_tests():
    tests = [
        test_recipe_set_covers_the_first_useful_language_families,
        test_recipe_set_defines_an_explainable_shot_record_selection,
        test_every_recipe_passes_the_renderer_neutral_contract,
        test_missing_lifecycle_phase_is_rejected,
        test_missing_reference_implementation_is_rejected,
        test_renderer_specific_recipe_is_rejected,
        test_nested_renderer_specific_recipe_is_rejected,
    ]
    for test in tests:
        test()
    print(f"PASS: renderer-neutral shot recipes ({len(tests)} checks)")


if __name__ == "__main__":
    run_tests()
