import copy
import json
import re
import unittest

from src.ai_report_contract import (
    AI_CREATOR_REPORT_SCHEMA_VERSION,
    AIReportValidationError,
    get_ai_creator_report_json_schema,
    validate_ai_creator_report,
)


def _valid_report(language: str = "en") -> dict:
    return {
        "schema_version": "1.0",
        "language": language,
        "executive_summary": "Performance is promising but evidence is limited.",
        "strengths": [
            {
                "title": "Strong save rate",
                "evidence": "The leading covers have above-portfolio save rates.",
                "interpretation": "The format may encourage repeat viewing.",
            }
        ],
        "risks": [
            {
                "title": "Small sample",
                "evidence": "The portfolio contains few comparable covers.",
                "mitigation": "Collect more observations before concluding.",
            }
        ],
        "recommended_actions": [
            {
                "action": "Run one controlled cover test.",
                "rationale": "A controlled test can strengthen the evidence.",
                "priority": "high",
            }
        ],
        "next_cover_strategy": {
            "recommendation": "Test the strongest observed format.",
            "reasoning": "It currently has the best supported evidence.",
            "confidence": "medium",
        },
        "data_limitations": ["Limited number of covers."],
    }


class AIReportContractTests(unittest.TestCase):
    def assert_validation_error(
        self,
        payload: object,
        expected_message: str,
    ) -> None:
        with self.assertRaisesRegex(
            AIReportValidationError,
            f"^{re.escape(expected_message)}$",
        ):
            validate_ai_creator_report(payload)

    def test_valid_english_report_passes(self) -> None:
        payload = _valid_report("en")

        self.assertEqual(validate_ai_creator_report(payload), payload)

    def test_valid_turkish_report_passes(self) -> None:
        payload = _valid_report("tr")
        payload["executive_summary"] = "Performans umut verici ancak veri sınırlı."
        payload["recommended_actions"][0]["action"] = "Kontrollü test yap."

        self.assertEqual(validate_ai_creator_report(payload), payload)

    def test_surrounding_whitespace_is_normalized(self) -> None:
        payload = _valid_report()
        payload["language"] = " en "
        payload["executive_summary"] = "  Summary  "
        payload["strengths"][0]["title"] = "  Strength  "
        payload["recommended_actions"][0]["priority"] = " high "
        payload["next_cover_strategy"]["confidence"] = " medium "
        payload["data_limitations"][0] = "  Limitation  "

        normalized = validate_ai_creator_report(payload)

        self.assertEqual(normalized["language"], "en")
        self.assertEqual(normalized["executive_summary"], "Summary")
        self.assertEqual(normalized["strengths"][0]["title"], "Strength")
        self.assertEqual(
            normalized["recommended_actions"][0]["priority"],
            "high",
        )
        self.assertEqual(
            normalized["next_cover_strategy"]["confidence"],
            "medium",
        )
        self.assertEqual(normalized["data_limitations"], ["Limitation"])

    def test_input_payload_is_not_mutated(self) -> None:
        payload = _valid_report()
        payload["executive_summary"] = "  Summary  "
        original = copy.deepcopy(payload)

        normalized = validate_ai_creator_report(payload)

        self.assertEqual(payload, original)
        self.assertIsNot(normalized, payload)
        self.assertIsNot(normalized["strengths"], payload["strengths"])

    def test_non_dictionary_payload_is_rejected(self) -> None:
        self.assert_validation_error([], "report: invalid_type")

    def test_missing_required_key_is_rejected(self) -> None:
        payload = _valid_report()
        del payload["next_cover_strategy"]

        self.assert_validation_error(
            payload,
            "report.next_cover_strategy: missing_key",
        )

    def test_unknown_top_level_key_is_rejected(self) -> None:
        payload = _valid_report()
        payload["extra"] = "value"

        self.assert_validation_error(payload, "report: unexpected_key")

    def test_unknown_nested_key_is_rejected(self) -> None:
        payload = _valid_report()
        payload["strengths"][0]["extra"] = "value"

        self.assert_validation_error(
            payload,
            "report.strengths[0]: unexpected_key",
        )

    def test_invalid_language_is_rejected(self) -> None:
        payload = _valid_report()
        payload["language"] = "de"

        self.assert_validation_error(
            payload,
            "report.language: invalid_value",
        )

    def test_invalid_priority_is_rejected(self) -> None:
        payload = _valid_report()
        payload["recommended_actions"][0]["priority"] = "urgent"

        self.assert_validation_error(
            payload,
            "report.recommended_actions[0].priority: invalid_value",
        )

    def test_invalid_confidence_is_rejected(self) -> None:
        payload = _valid_report()
        payload["next_cover_strategy"]["confidence"] = "certain"

        self.assert_validation_error(
            payload,
            "report.next_cover_strategy.confidence: invalid_value",
        )

    def test_empty_required_string_is_rejected(self) -> None:
        payload = _valid_report()
        payload["strengths"][0]["title"] = "  "

        self.assert_validation_error(
            payload,
            "report.strengths[0].title: empty_string",
        )

    def test_incorrect_list_and_object_types_are_rejected(self) -> None:
        cases = [
            ("strengths", {}, "report.strengths: invalid_type"),
            ("risks", {}, "report.risks: invalid_type"),
            (
                "recommended_actions",
                {},
                "report.recommended_actions: invalid_type",
            ),
            (
                "next_cover_strategy",
                [],
                "report.next_cover_strategy: invalid_type",
            ),
            (
                "data_limitations",
                {},
                "report.data_limitations: invalid_type",
            ),
        ]

        for key, invalid_value, message in cases:
            with self.subTest(key=key):
                payload = _valid_report()
                payload[key] = invalid_value
                self.assert_validation_error(payload, message)

    def test_list_size_limits_are_enforced(self) -> None:
        strength = _valid_report()["strengths"][0]
        risk = _valid_report()["risks"][0]
        action = _valid_report()["recommended_actions"][0]
        cases = [
            (
                "strengths",
                [copy.deepcopy(strength) for _ in range(4)],
                "report.strengths: too_many_items",
            ),
            (
                "risks",
                [copy.deepcopy(risk) for _ in range(4)],
                "report.risks: too_many_items",
            ),
            (
                "recommended_actions",
                [],
                "report.recommended_actions: too_few_items",
            ),
            (
                "recommended_actions",
                [copy.deepcopy(action) for _ in range(6)],
                "report.recommended_actions: too_many_items",
            ),
            (
                "data_limitations",
                [f"Limitation {index}" for index in range(6)],
                "report.data_limitations: too_many_items",
            ),
        ]

        for key, invalid_value, message in cases:
            with self.subTest(key=key, message=message):
                payload = _valid_report()
                payload[key] = invalid_value
                self.assert_validation_error(payload, message)

    def test_json_schema_is_serializable_and_matches_version(self) -> None:
        schema = get_ai_creator_report_json_schema()

        self.assertIsInstance(json.dumps(schema), str)
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            AI_CREATOR_REPORT_SCHEMA_VERSION,
        )

    def test_json_schema_calls_return_independent_dictionaries(self) -> None:
        first = get_ai_creator_report_json_schema()
        second = get_ai_creator_report_json_schema()

        first["properties"]["language"]["enum"].append("de")

        self.assertIsNot(first, second)
        self.assertEqual(second["properties"]["language"]["enum"], ["en", "tr"])

    def test_json_schema_disallows_additional_properties_everywhere(self) -> None:
        schema = get_ai_creator_report_json_schema()
        object_schemas = [
            schema,
            schema["properties"]["strengths"]["items"],
            schema["properties"]["risks"]["items"],
            schema["properties"]["recommended_actions"]["items"],
            schema["properties"]["next_cover_strategy"],
        ]

        for object_schema in object_schemas:
            with self.subTest(properties=list(object_schema["properties"])):
                self.assertIs(object_schema["additionalProperties"], False)
                self.assertEqual(
                    object_schema["required"],
                    list(object_schema["properties"]),
                )


if __name__ == "__main__":
    unittest.main()
