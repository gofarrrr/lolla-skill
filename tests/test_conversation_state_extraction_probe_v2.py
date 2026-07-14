from __future__ import annotations

from scripts.evals import run_conversation_state_extraction_probe as v1
from scripts.evals import run_conversation_state_extraction_probe_v2 as v2


def test_v2_changes_only_const_to_single_value_enum() -> None:
    old = v1.response_schema()
    new = v2.response_schema()
    old_version = old["schema"]["properties"]["schema_version"]
    new_version = new["schema"]["properties"]["schema_version"]
    assert old_version == {"type": "string", "const": v1.RAW_OUTPUT_SCHEMA}
    assert new_version == {"type": "string", "enum": [v1.RAW_OUTPUT_SCHEMA]}
    old["schema"]["properties"]["schema_version"] = new_version
    assert old == new


def test_v2_schema_uses_only_documented_gemini_schema_keywords() -> None:
    allowed = {
        "type",
        "format",
        "title",
        "description",
        "enum",
        "items",
        "prefixItems",
        "minItems",
        "maxItems",
        "minimum",
        "maximum",
        "anyOf",
        "oneOf",
        "properties",
        "additionalProperties",
        "required",
    }

    def visit(node: object) -> None:
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if key not in {"name", "strict", "schema"}:
                assert key in allowed
            if key == "properties":
                for child in value.values():
                    visit(child)
            elif key in {"items"}:
                visit(value)
            elif key in {"anyOf", "oneOf", "prefixItems"}:
                for child in value:
                    visit(child)

    visit(v2.response_schema()["schema"])
