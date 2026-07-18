"""Structured report contract for the future AI Creator Coach."""

from __future__ import annotations

from typing import Any


AI_CREATOR_REPORT_SCHEMA_VERSION = "1.0"

_REPORT_KEYS = (
    "schema_version",
    "language",
    "executive_summary",
    "strengths",
    "risks",
    "recommended_actions",
    "next_cover_strategy",
    "data_limitations",
)
_STRENGTH_KEYS = ("title", "evidence", "interpretation")
_RISK_KEYS = ("title", "evidence", "mitigation")
_ACTION_KEYS = ("action", "rationale", "priority")
_STRATEGY_KEYS = ("recommendation", "reasoning", "confidence")

_LANGUAGES = {"en", "tr"}
_PRIORITIES = {"high", "medium", "low"}
_CONFIDENCE_LEVELS = {"high", "medium", "low"}


class AIReportValidationError(ValueError):
    """Raised when an AI Creator Coach report violates its contract."""


def _raise_validation_error(path: str, code: str) -> None:
    raise AIReportValidationError(f"{path}: {code}")


def _validate_object(
    value: object,
    path: str,
    required_keys: tuple[str, ...],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _raise_validation_error(path, "invalid_type")

    for key in required_keys:
        if key not in value:
            _raise_validation_error(f"{path}.{key}", "missing_key")

    if set(value) != set(required_keys):
        _raise_validation_error(path, "unexpected_key")

    return value


def _validate_text(value: object, path: str) -> str:
    if not isinstance(value, str):
        _raise_validation_error(path, "invalid_type")

    normalized = value.strip()
    if not normalized:
        _raise_validation_error(path, "empty_string")

    return normalized


def _validate_enum(
    value: object,
    path: str,
    allowed_values: set[str],
) -> str:
    normalized = _validate_text(value, path)
    if normalized not in allowed_values:
        _raise_validation_error(path, "invalid_value")

    return normalized


def _validate_list(
    value: object,
    path: str,
    *,
    minimum: int = 0,
    maximum: int,
) -> list[Any]:
    if not isinstance(value, list):
        _raise_validation_error(path, "invalid_type")

    if len(value) < minimum:
        _raise_validation_error(path, "too_few_items")

    if len(value) > maximum:
        _raise_validation_error(path, "too_many_items")

    return value


def _validate_text_object(
    value: object,
    path: str,
    keys: tuple[str, ...],
) -> dict[str, str]:
    item = _validate_object(value, path, keys)
    return {
        key: _validate_text(item[key], f"{path}.{key}")
        for key in keys
    }


def _validate_strengths(value: object) -> list[dict[str, str]]:
    strengths = _validate_list(value, "report.strengths", maximum=3)
    return [
        _validate_text_object(
            strength,
            f"report.strengths[{index}]",
            _STRENGTH_KEYS,
        )
        for index, strength in enumerate(strengths)
    ]


def _validate_risks(value: object) -> list[dict[str, str]]:
    risks = _validate_list(value, "report.risks", maximum=3)
    return [
        _validate_text_object(
            risk,
            f"report.risks[{index}]",
            _RISK_KEYS,
        )
        for index, risk in enumerate(risks)
    ]


def _validate_actions(value: object) -> list[dict[str, str]]:
    actions = _validate_list(
        value,
        "report.recommended_actions",
        minimum=1,
        maximum=5,
    )
    normalized_actions: list[dict[str, str]] = []

    for index, action_value in enumerate(actions):
        path = f"report.recommended_actions[{index}]"
        action = _validate_object(action_value, path, _ACTION_KEYS)
        normalized_actions.append(
            {
                "action": _validate_text(action["action"], f"{path}.action"),
                "rationale": _validate_text(
                    action["rationale"],
                    f"{path}.rationale",
                ),
                "priority": _validate_enum(
                    action["priority"],
                    f"{path}.priority",
                    _PRIORITIES,
                ),
            }
        )

    return normalized_actions


def _validate_strategy(value: object) -> dict[str, str]:
    path = "report.next_cover_strategy"
    strategy = _validate_object(value, path, _STRATEGY_KEYS)
    return {
        "recommendation": _validate_text(
            strategy["recommendation"],
            f"{path}.recommendation",
        ),
        "reasoning": _validate_text(
            strategy["reasoning"],
            f"{path}.reasoning",
        ),
        "confidence": _validate_enum(
            strategy["confidence"],
            f"{path}.confidence",
            _CONFIDENCE_LEVELS,
        ),
    }


def _validate_limitations(value: object) -> list[str]:
    limitations = _validate_list(
        value,
        "report.data_limitations",
        maximum=5,
    )
    return [
        _validate_text(limitation, f"report.data_limitations[{index}]")
        for index, limitation in enumerate(limitations)
    ]


def _non_empty_string_schema() -> dict[str, Any]:
    return {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S",
    }


def _strict_object_schema(
    properties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def get_ai_creator_report_json_schema() -> dict:
    """Return a fresh strict JSON Schema for AI Creator Coach reports."""
    strength_schema = _strict_object_schema(
        {
            "title": _non_empty_string_schema(),
            "evidence": _non_empty_string_schema(),
            "interpretation": _non_empty_string_schema(),
        }
    )
    risk_schema = _strict_object_schema(
        {
            "title": _non_empty_string_schema(),
            "evidence": _non_empty_string_schema(),
            "mitigation": _non_empty_string_schema(),
        }
    )
    action_schema = _strict_object_schema(
        {
            "action": _non_empty_string_schema(),
            "rationale": _non_empty_string_schema(),
            "priority": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
        }
    )
    strategy_schema = _strict_object_schema(
        {
            "recommendation": _non_empty_string_schema(),
            "reasoning": _non_empty_string_schema(),
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
        }
    )

    return _strict_object_schema(
        {
            "schema_version": {
                "type": "string",
                "const": AI_CREATOR_REPORT_SCHEMA_VERSION,
            },
            "language": {
                "type": "string",
                "enum": ["en", "tr"],
            },
            "executive_summary": _non_empty_string_schema(),
            "strengths": {
                "type": "array",
                "items": strength_schema,
                "maxItems": 3,
            },
            "risks": {
                "type": "array",
                "items": risk_schema,
                "maxItems": 3,
            },
            "recommended_actions": {
                "type": "array",
                "items": action_schema,
                "minItems": 1,
                "maxItems": 5,
            },
            "next_cover_strategy": strategy_schema,
            "data_limitations": {
                "type": "array",
                "items": _non_empty_string_schema(),
                "maxItems": 5,
            },
        }
    )


def validate_ai_creator_report(payload: object) -> dict:
    """Validate and normalize an AI Creator Coach report payload."""
    report = _validate_object(payload, "report", _REPORT_KEYS)

    schema_version = report["schema_version"]
    if not isinstance(schema_version, str):
        _raise_validation_error("report.schema_version", "invalid_type")
    if schema_version != AI_CREATOR_REPORT_SCHEMA_VERSION:
        _raise_validation_error("report.schema_version", "invalid_value")

    return {
        "schema_version": schema_version,
        "language": _validate_enum(
            report["language"],
            "report.language",
            _LANGUAGES,
        ),
        "executive_summary": _validate_text(
            report["executive_summary"],
            "report.executive_summary",
        ),
        "strengths": _validate_strengths(report["strengths"]),
        "risks": _validate_risks(report["risks"]),
        "recommended_actions": _validate_actions(
            report["recommended_actions"]
        ),
        "next_cover_strategy": _validate_strategy(
            report["next_cover_strategy"]
        ),
        "data_limitations": _validate_limitations(
            report["data_limitations"]
        ),
    }
