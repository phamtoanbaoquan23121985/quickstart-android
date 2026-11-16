"""Fail-closed selection of approved physical Pixel targets from Test Lab."""
from __future__ import annotations

REQUIRED_TARGETS = {"Pixel 10 Pro": "blazer", "Pixel 10 Pro XL": "mustang"}
REQUIRED_API = "36"


def select_supported_devices(catalog: list[dict]) -> list[dict]:
    """Select exact physical targets only; reject unknown or partial evidence."""
    selected = []
    for target_name, expected_codename in REQUIRED_TARGETS.items():
        matches = [item for item in catalog if item.get("name") == target_name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one catalog entry for {target_name}")
        item = matches[0]
        model_id = item.get("id") or item.get("modelId")
        versions = item.get("supportedVersionIds")
        form = item.get("form") or item.get("formFactor")
        codename = item.get("codename")
        if not model_id or not isinstance(versions, list) or not form or not codename:
            raise ValueError(f"Incomplete Firebase Test Lab catalog entry: {target_name}")
        if str(form).upper() != "PHYSICAL":
            raise ValueError(f"Refusing non-physical device: {target_name}")
        if codename != expected_codename:
            raise ValueError(
                f"Codename mismatch for {target_name}: expected {expected_codename}, got {codename}"
            )
        if REQUIRED_API not in {str(version) for version in versions}:
            raise ValueError(f"{target_name} does not advertise Android API {REQUIRED_API}")
        selected.append({
            "name": target_name,
            "model_id": model_id,
            "expected_codename": expected_codename,
            "api_level": int(REQUIRED_API),
            "physical_device_required": True,
        })
    return selected


def main() -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("catalog_json", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog = json.loads(args.catalog_json.read_text(encoding="utf-8"))
    if isinstance(catalog, dict):
        catalog = catalog.get("models", catalog.get("devices", []))
    if not isinstance(catalog, list):
        raise ValueError("Unrecognized Firebase Test Lab model catalog format")
    selected = select_supported_devices(catalog)
    args.output.write_text(json.dumps(selected, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(selected)} exact physical Pixel targets for API {REQUIRED_API}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
