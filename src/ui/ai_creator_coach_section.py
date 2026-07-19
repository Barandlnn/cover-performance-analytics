"""Streamlit UI section for the AI Creator Coach report."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, MutableMapping
from typing import Any

import pandas as pd
import streamlit as st

from src.ai_context_builder import build_ai_creator_context
from src.ai_creator_service import (
    DEFAULT_AI_MODEL,
    AICreatorConfigurationError,
    AICreatorResponseError,
    AICreatorServiceError,
    generate_ai_creator_report,
)
from src.i18n import t


_REPORT_SESSION_KEY = "ai_creator_coach.report"
_CACHE_KEY_SESSION_KEY = "ai_creator_coach.cache_key"

_LIMITATION_TRANSLATION_KEYS = {
    "empty_dataset": "ai_creator_coach.limitation.empty_dataset",
    "insufficient_cover_count": (
        "ai_creator_coach.limitation.insufficient_cover_count"
    ),
    "missing_performance_score": (
        "ai_creator_coach.limitation.missing_performance_score"
    ),
    "missing_analysis_metrics": (
        "ai_creator_coach.limitation.missing_analysis_metrics"
    ),
    "limited_group_comparison": (
        "ai_creator_coach.limitation.limited_group_comparison"
    ),
    "low_view_rate_outlier": (
        "ai_creator_coach.limitation.low_view_rate_outlier"
    ),
}

_ERROR_TRANSLATION_KEYS = {
    "configuration_error": "ai_creator_coach.error.configuration",
    "invalid_response_error": "ai_creator_coach.error.invalid_response",
    "api_request_error": "ai_creator_coach.error.api_request",
    "unexpected_error": "ai_creator_coach.error.unexpected",
}

_LEVEL_TRANSLATION_KEYS = {
    "high": "ai_creator_coach.level.high",
    "medium": "ai_creator_coach.level.medium",
    "low": "ai_creator_coach.level.low",
}


def _build_report_cache_key(
    context: dict,
    language: str,
    model: str = DEFAULT_AI_MODEL,
) -> str:
    """Build a stable cache key for the current report inputs."""
    serialized = json.dumps(
        {
            "context": context,
            "language": language,
            "model": model,
        },
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _read_api_key(secrets: object) -> str:
    """Read and normalize the API key without exposing secret values."""
    try:
        value = secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""

    return value.strip() if isinstance(value, str) else ""


def _get_generation_blocker(
    cover_data: pd.DataFrame,
    context: dict,
    api_key: str,
) -> str | None:
    if cover_data.empty:
        return "empty_data"

    if not api_key:
        return "missing_api_key"

    if not context.get("data_quality", {}).get("is_sufficient", False):
        return "insufficient_data"

    return None


def _prepare_section_inputs(
    cover_data: pd.DataFrame,
    language: str,
    secrets: object,
) -> tuple[dict, str, str, str | None]:
    """Build local context, cache identity, and generation eligibility."""
    context = build_ai_creator_context(cover_data)
    api_key = _read_api_key(secrets)
    cache_key = _build_report_cache_key(
        context,
        language,
        DEFAULT_AI_MODEL,
    )
    blocker = _get_generation_blocker(cover_data, context, api_key)
    return context, api_key, cache_key, blocker


def _store_cached_report(
    session_state: MutableMapping[str, Any],
    report: dict,
    cache_key: str,
) -> None:
    """Store only a validated report copy and its matching cache key."""
    session_state[_REPORT_SESSION_KEY] = copy.deepcopy(report)
    session_state[_CACHE_KEY_SESSION_KEY] = cache_key


def _get_current_report(
    session_state: MutableMapping[str, Any],
    cache_key: str,
) -> dict | None:
    if session_state.get(_CACHE_KEY_SESSION_KEY) != cache_key:
        return None

    report = session_state.get(_REPORT_SESSION_KEY)
    return copy.deepcopy(report) if isinstance(report, dict) else None


def _has_stale_report(
    session_state: MutableMapping[str, Any],
    cache_key: str,
) -> bool:
    return (
        isinstance(session_state.get(_REPORT_SESSION_KEY), dict)
        and session_state.get(_CACHE_KEY_SESSION_KEY) != cache_key
    )


def _generate_report_if_requested(
    *,
    button_clicked: bool,
    blocker: str | None,
    context: dict,
    language: str,
    api_key: str,
    cache_key: str,
    session_state: MutableMapping[str, Any],
    report_generator: Callable[..., dict] = generate_ai_creator_report,
) -> str | None:
    """Run at most one report request and return a stable UI error code."""
    if not button_clicked or blocker is not None:
        return None

    try:
        report = report_generator(
            context=context,
            language=language,
            api_key=api_key,
            model=DEFAULT_AI_MODEL,
        )
    except AICreatorConfigurationError:
        return "configuration_error"
    except AICreatorResponseError:
        return "invalid_response_error"
    except AICreatorServiceError:
        return "api_request_error"
    except Exception:
        return "unexpected_error"

    _store_cached_report(session_state, report, cache_key)
    return None


def _translate_level(level: str, language: str) -> str:
    translation_key = _LEVEL_TRANSLATION_KEYS.get(
        level,
        "ai_creator_coach.level.low",
    )
    return t(translation_key, language)


def _render_local_scope(context: dict, language: str) -> None:
    cover_count = context.get("data_summary", {}).get("cover_count", 0)
    st.write(
        t("ai_creator_coach.analyzed_cover_count", language).format(
            cover_count=cover_count,
        )
    )

    limitations = context.get("data_quality", {}).get("limitations", [])
    if not limitations:
        return

    with st.expander(t("ai_creator_coach.local_limitations", language)):
        for limitation in limitations:
            translation_key = _LIMITATION_TRANSLATION_KEYS.get(
                limitation,
                "ai_creator_coach.limitation.unknown",
            )
            st.write(t(translation_key, language))


def _render_report(report: dict, language: str) -> None:
    st.subheader(t("ai_creator_coach.executive_summary", language))
    st.write(report["executive_summary"])

    st.subheader(t("ai_creator_coach.strengths", language))
    if not report["strengths"]:
        st.info(t("common.no_data", language))
    for strength in report["strengths"]:
        st.success(strength["title"])
        st.caption(t("ai_creator_coach.evidence", language))
        st.write(strength["evidence"])
        st.caption(t("ai_creator_coach.interpretation", language))
        st.write(strength["interpretation"])

    st.subheader(t("ai_creator_coach.risks", language))
    if not report["risks"]:
        st.info(t("common.no_data", language))
    for risk in report["risks"]:
        st.warning(risk["title"])
        st.caption(t("ai_creator_coach.evidence", language))
        st.write(risk["evidence"])
        st.caption(t("ai_creator_coach.mitigation", language))
        st.write(risk["mitigation"])

    st.subheader(t("ai_creator_coach.recommended_actions", language))
    for action in report["recommended_actions"]:
        with st.expander(action["action"], expanded=True):
            st.caption(t("ai_creator_coach.rationale", language))
            st.write(action["rationale"])
            st.caption(t("ai_creator_coach.priority", language))
            st.write(_translate_level(action["priority"], language))

    st.subheader(t("ai_creator_coach.next_cover_strategy", language))
    strategy = report["next_cover_strategy"]
    st.caption(t("ai_creator_coach.recommendation", language))
    st.info(strategy["recommendation"])
    st.caption(t("ai_creator_coach.reasoning", language))
    st.write(strategy["reasoning"])
    st.caption(t("ai_creator_coach.confidence", language))
    st.write(_translate_level(strategy["confidence"], language))

    st.subheader(t("ai_creator_coach.data_limitations", language))
    if not report["data_limitations"]:
        st.info(t("common.no_data", language))
    for limitation in report["data_limitations"]:
        st.warning(limitation)


def render_ai_creator_coach_section(
    cover_data: pd.DataFrame,
    language: str,
) -> None:
    """Render the filter-aware AI Creator Coach section."""
    st.divider()
    st.subheader(t("ai_creator_coach.title", language))
    st.caption(t("ai_creator_coach.caption", language))

    context, api_key, cache_key, blocker = _prepare_section_inputs(
        cover_data,
        language,
        st.secrets,
    )
    _render_local_scope(context, language)

    blocker_messages = {
        "empty_data": "ai_creator_coach.empty_data",
        "missing_api_key": "ai_creator_coach.missing_api_key",
        "insufficient_data": "ai_creator_coach.insufficient_data",
    }
    if blocker is not None:
        st.warning(t(blocker_messages[blocker], language))

    current_report = _get_current_report(st.session_state, cache_key)
    if current_report is None and _has_stale_report(st.session_state, cache_key):
        st.info(t("ai_creator_coach.stale_report", language))

    button_key = (
        "ai_creator_coach.regenerate_report"
        if current_report is not None
        else "ai_creator_coach.generate_report"
    )
    button_clicked = st.button(
        t(button_key, language),
        disabled=blocker is not None,
    )

    error_code = None
    if button_clicked and blocker is None:
        with st.spinner(t("ai_creator_coach.generating_report", language)):
            error_code = _generate_report_if_requested(
                button_clicked=True,
                blocker=None,
                context=context,
                language=language,
                api_key=api_key,
                cache_key=cache_key,
                session_state=st.session_state,
            )

        if error_code is None:
            st.success(t("ai_creator_coach.report_generated", language))
        else:
            st.error(t(_ERROR_TRANSLATION_KEYS[error_code], language))

    current_report = _get_current_report(st.session_state, cache_key)
    if current_report is not None:
        _render_report(current_report, language)
