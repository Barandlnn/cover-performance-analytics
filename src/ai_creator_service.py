"""OpenAI Responses API service for AI Creator Coach reports."""

from __future__ import annotations

import json

from openai import OpenAI

from src.ai_report_contract import (
    AIReportValidationError,
    get_ai_creator_report_json_schema,
    validate_ai_creator_report,
)


DEFAULT_AI_MODEL = "gpt-5.6-sol"

_DEVELOPER_INSTRUCTIONS = """Generate an AI Creator Coach report using only the supplied deterministic context.
Never invent metrics, and never recalculate or alter supplied metrics.
Do not make causal claims; describe correlations only as directional observations.
Explicitly respect evidence_quality and evidence_flags. Treat low_view_sample as low-confidence evidence.
Mention relevant data_quality.limitations in the report.
Return content in the requested language.
Keep recommendations actionable and evidence-based.
Return only the structured JSON response and do not use Markdown.
"""


class AICreatorServiceError(RuntimeError):
    """Base error for AI Creator Coach service failures."""


class AICreatorConfigurationError(AICreatorServiceError):
    """Raised when local service inputs are invalid."""


class AICreatorResponseError(AICreatorServiceError):
    """Raised when a model response cannot produce a valid report."""


def _validate_configuration(
    context: object,
    language: object,
    api_key: object,
    model: object,
) -> tuple[dict, str, str, str]:
    if not isinstance(context, dict):
        raise AICreatorConfigurationError("ai_service.context: invalid_type")

    if not isinstance(language, str) or language.strip() not in {"en", "tr"}:
        raise AICreatorConfigurationError("ai_service.language: invalid_value")

    if not isinstance(api_key, str) or not api_key.strip():
        raise AICreatorConfigurationError("ai_service.api_key: missing")

    if not isinstance(model, str) or not model.strip():
        raise AICreatorConfigurationError("ai_service.model: missing")

    return context, language.strip(), api_key.strip(), model.strip()


def _serialize_context(context: dict) -> str:
    try:
        return json.dumps(
            context,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise AICreatorConfigurationError(
            "ai_service.context: not_serializable"
        ) from exc


def _build_user_message(context_json: str, language: str) -> str:
    return (
        f"Requested report language: {language}\n"
        f"Deterministic analytics context:\n{context_json}"
    )


def _build_text_format() -> dict:
    return {
        "format": {
            "type": "json_schema",
            "name": "ai_creator_report",
            "strict": True,
            "schema": get_ai_creator_report_json_schema(),
        }
    }


def _parse_response(response: object) -> dict:
    output_text = getattr(response, "output_text", None)
    if not isinstance(output_text, str) or not output_text.strip():
        raise AICreatorResponseError("ai_service.response: empty_output")

    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise AICreatorResponseError(
            "ai_service.response: invalid_json"
        ) from exc

    try:
        return validate_ai_creator_report(payload)
    except AIReportValidationError as exc:
        raise AICreatorResponseError(
            "ai_service.response: contract_validation_failed"
        ) from exc


def generate_ai_creator_report(
    context: dict,
    language: str,
    api_key: str,
    model: str = DEFAULT_AI_MODEL,
    client: object | None = None,
) -> dict:
    """Generate and locally validate a structured AI Creator Coach report."""
    context, language, api_key, model = _validate_configuration(
        context,
        language,
        api_key,
        model,
    )
    context_json = _serialize_context(context)
    service_client = client if client is not None else OpenAI(api_key=api_key)

    try:
        response = service_client.responses.create(
            model=model,
            reasoning={
                "mode": "standard",
                "effort": "low",
            },
            instructions=_DEVELOPER_INSTRUCTIONS,
            input=_build_user_message(context_json, language),
            text=_build_text_format(),
        )
    except Exception as exc:
        raise AICreatorServiceError("ai_service.request: failed") from exc

    return _parse_response(response)
