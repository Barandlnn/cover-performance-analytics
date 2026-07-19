import copy
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.ai_creator_service import (
    DEFAULT_AI_MODEL,
    AICreatorConfigurationError,
    AICreatorResponseError,
    AICreatorServiceError,
)
from src.ui.ai_creator_coach_section import (
    _CACHE_KEY_SESSION_KEY,
    _REPORT_SESSION_KEY,
    _build_report_cache_key,
    _generate_report_if_requested,
    _get_current_report,
    _get_generation_blocker,
    _has_stale_report,
    _prepare_section_inputs,
    _read_api_key,
    _store_cached_report,
)


def _context(*, sufficient: bool = True, cover_count: int = 3) -> dict:
    return {
        "context_version": "1.0",
        "data_summary": {"cover_count": cover_count},
        "portfolio_metrics": {"median_views": 1000},
        "top_covers": [],
        "group_performance": {},
        "data_quality": {
            "is_sufficient": sufficient,
            "limitations": [],
            "missing_columns": [],
        },
    }


def _report() -> dict:
    return {
        "schema_version": "1.0",
        "language": "en",
        "executive_summary": "Summary",
        "strengths": [],
        "risks": [],
        "recommended_actions": [
            {
                "action": "Test",
                "rationale": "Evidence",
                "priority": "high",
            }
        ],
        "next_cover_strategy": {
            "recommendation": "Test",
            "reasoning": "Evidence",
            "confidence": "medium",
        },
        "data_limitations": [],
    }


class RaisingSecrets:
    def get(self, key, default=None):
        raise FileNotFoundError("secrets unavailable")


class AICreatorCoachSectionTests(unittest.TestCase):
    def test_cache_key_is_deterministic_for_equivalent_contexts(self) -> None:
        first = {"b": 2, "a": {"y": "Türkçe", "x": 1}}
        second = {"a": {"x": 1, "y": "Türkçe"}, "b": 2}

        self.assertEqual(
            _build_report_cache_key(first, "tr"),
            _build_report_cache_key(second, "tr"),
        )

    def test_cache_key_changes_when_context_changes(self) -> None:
        self.assertNotEqual(
            _build_report_cache_key({"value": 1}, "en"),
            _build_report_cache_key({"value": 2}, "en"),
        )

    def test_cache_key_changes_when_language_changes(self) -> None:
        context = {"value": 1}
        self.assertNotEqual(
            _build_report_cache_key(context, "en"),
            _build_report_cache_key(context, "tr"),
        )

    def test_cache_key_uses_default_model(self) -> None:
        context = {"value": 1}
        default_key = _build_report_cache_key(context, "en")

        self.assertEqual(
            default_key,
            _build_report_cache_key(context, "en", DEFAULT_AI_MODEL),
        )
        self.assertNotEqual(
            default_key,
            _build_report_cache_key(context, "en", "different-model"),
        )

    def test_missing_api_key_is_handled_safely(self) -> None:
        self.assertEqual(_read_api_key({}), "")
        self.assertEqual(_read_api_key(RaisingSecrets()), "")

    def test_insufficient_data_blocks_generation(self) -> None:
        data = pd.DataFrame({"cover_id": ["C1", "C2"]})
        self.assertEqual(
            _get_generation_blocker(data, _context(sufficient=False), "key"),
            "insufficient_data",
        )

    def test_empty_data_blocks_generation(self) -> None:
        self.assertEqual(
            _get_generation_blocker(pd.DataFrame(), _context(), "key"),
            "empty_data",
        )

    def test_matching_cached_report_can_be_stored_and_retrieved(self) -> None:
        session_state = {}
        report = _report()

        _store_cached_report(session_state, report, "cache-key")

        self.assertEqual(
            _get_current_report(session_state, "cache-key"),
            report,
        )

    def test_stale_cached_report_is_not_current(self) -> None:
        session_state = {}
        _store_cached_report(session_state, _report(), "old-key")

        self.assertIsNone(_get_current_report(session_state, "new-key"))
        self.assertTrue(_has_stale_report(session_state, "new-key"))

    def test_one_button_click_calls_generator_exactly_once(self) -> None:
        calls = []

        def generator(**kwargs):
            calls.append(kwargs)
            return _report()

        session_state = {}
        error = _generate_report_if_requested(
            button_clicked=True,
            blocker=None,
            context=_context(),
            language="en",
            api_key="test-key",
            cache_key="cache-key",
            session_state=session_state,
            report_generator=generator,
        )

        self.assertIsNone(error)
        self.assertEqual(len(calls), 1)
        self.assertEqual(session_state[_CACHE_KEY_SESSION_KEY], "cache-key")

    def test_normal_rerun_without_click_does_not_call_generator(self) -> None:
        calls = []

        def generator(**kwargs):
            calls.append(kwargs)
            return _report()

        _generate_report_if_requested(
            button_clicked=False,
            blocker=None,
            context=_context(),
            language="en",
            api_key="test-key",
            cache_key="cache-key",
            session_state={},
            report_generator=generator,
        )

        self.assertEqual(calls, [])

    def test_api_key_is_not_stored_in_session_state(self) -> None:
        session_state = {}
        api_key = "sensitive-test-key"

        _generate_report_if_requested(
            button_clicked=True,
            blocker=None,
            context=_context(),
            language="en",
            api_key=api_key,
            cache_key="cache-key",
            session_state=session_state,
            report_generator=lambda **kwargs: _report(),
        )

        self.assertEqual(
            set(session_state),
            {_REPORT_SESSION_KEY, _CACHE_KEY_SESSION_KEY},
        )
        self.assertNotIn(api_key, session_state.values())

    def test_service_exceptions_map_to_stable_ui_error_states(self) -> None:
        cases = [
            (
                AICreatorConfigurationError("configuration"),
                "configuration_error",
            ),
            (AICreatorResponseError("response"), "invalid_response_error"),
            (AICreatorServiceError("request"), "api_request_error"),
            (RuntimeError("unexpected"), "unexpected_error"),
        ]

        for exception, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                def generator(**kwargs):
                    raise exception

                error = _generate_report_if_requested(
                    button_clicked=True,
                    blocker=None,
                    context=_context(),
                    language="en",
                    api_key="test-key",
                    cache_key="cache-key",
                    session_state={},
                    report_generator=generator,
                )
                self.assertEqual(error, expected_error)

    def test_inputs_and_cached_report_are_not_mutated(self) -> None:
        data = pd.DataFrame(
            {
                "cover_id": ["C1", "C2", "C3"],
                "views": [100, 200, 300],
                "performance_score": [10, 20, 30],
            }
        )
        original_data = data.copy(deep=True)
        report = _report()
        original_report = copy.deepcopy(report)
        session_state = {}

        _prepare_section_inputs(data, "en", {"OPENAI_API_KEY": "test-key"})
        _store_cached_report(session_state, report, "cache-key")
        session_state[_REPORT_SESSION_KEY]["executive_summary"] = "Changed"

        assert_frame_equal(data, original_data)
        self.assertEqual(report, original_report)

    def test_both_languages_are_passed_to_service(self) -> None:
        received_languages = []

        def generator(**kwargs):
            received_languages.append(kwargs["language"])
            report = _report()
            report["language"] = kwargs["language"]
            return report

        for language in ["en", "tr"]:
            _generate_report_if_requested(
                button_clicked=True,
                blocker=None,
                context=_context(),
                language=language,
                api_key="test-key",
                cache_key=f"key-{language}",
                session_state={},
                report_generator=generator,
            )

        self.assertEqual(received_languages, ["en", "tr"])


if __name__ == "__main__":
    unittest.main()
