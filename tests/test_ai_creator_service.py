import copy
import json
import unittest

from src.ai_creator_service import (
    DEFAULT_AI_MODEL,
    AICreatorConfigurationError,
    AICreatorResponseError,
    AICreatorServiceError,
    generate_ai_creator_report,
)
from src.ai_report_contract import get_ai_creator_report_json_schema


def _valid_report(language: str = "en") -> dict:
    return {
        "schema_version": "1.0",
        "language": language,
        "executive_summary": "  Evidence supports a cautious test.  ",
        "strengths": [
            {
                "title": "Strong save rate",
                "evidence": "The supplied context shows a higher save rate.",
                "interpretation": "This is a directional observation.",
            }
        ],
        "risks": [
            {
                "title": "Limited evidence",
                "evidence": "The context flags a small sample.",
                "mitigation": "Collect more comparable observations.",
            }
        ],
        "recommended_actions": [
            {
                "action": "Run a controlled cover test.",
                "rationale": "It can strengthen the evidence.",
                "priority": "high",
            }
        ],
        "next_cover_strategy": {
            "recommendation": "Test the strongest supported format.",
            "reasoning": "It has the best directional evidence.",
            "confidence": "medium",
        },
        "data_limitations": ["The sample is limited."],
    }


class FakeResponses:
    def __init__(self, response: object = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response: object = None, error: Exception | None = None):
        self.responses = FakeResponses(response=response, error=error)


class FakeResponse:
    def __init__(self, output_text: str):
        self.output_text = output_text


class AICreatorServiceTests(unittest.TestCase):
    api_key = "test-secret-api-key"

    def make_client(self, report: dict | None = None) -> FakeClient:
        payload = report if report is not None else _valid_report()
        return FakeClient(FakeResponse(json.dumps(payload, ensure_ascii=False)))

    def call_service(
        self,
        client: FakeClient,
        *,
        context: dict | None = None,
        language: str = "en",
        api_key: str | None = None,
        model: str = DEFAULT_AI_MODEL,
    ) -> dict:
        return generate_ai_creator_report(
            context=context if context is not None else {"cover_count": 3},
            language=language,
            api_key=self.api_key if api_key is None else api_key,
            model=model,
            client=client,
        )

    def test_valid_english_response_is_returned_and_normalized(self) -> None:
        client = self.make_client(_valid_report("en"))

        report = self.call_service(client)

        self.assertEqual(report["language"], "en")
        self.assertEqual(
            report["executive_summary"],
            "Evidence supports a cautious test.",
        )

    def test_valid_turkish_response_is_returned_and_normalized(self) -> None:
        report_payload = _valid_report("tr")
        report_payload["executive_summary"] = "  Kanıt kontrollü testi destekliyor.  "
        client = self.make_client(report_payload)

        report = self.call_service(client, language="tr")

        self.assertEqual(report["language"], "tr")
        self.assertEqual(
            report["executive_summary"],
            "Kanıt kontrollü testi destekliyor.",
        )

    def test_supplied_client_receives_responses_create_call(self) -> None:
        client = self.make_client()

        self.call_service(client)

        self.assertEqual(len(client.responses.calls), 1)

    def test_default_model_is_used(self) -> None:
        client = self.make_client()

        self.call_service(client)

        self.assertEqual(
            client.responses.calls[0]["model"],
            "gpt-5.6-sol",
        )

    def test_custom_model_is_respected(self) -> None:
        client = self.make_client()

        self.call_service(client, model="custom-model")

        self.assertEqual(client.responses.calls[0]["model"], "custom-model")

    def test_reasoning_mode_and_effort_are_configured(self) -> None:
        client = self.make_client()

        self.call_service(client)

        self.assertEqual(
            client.responses.calls[0]["reasoning"],
            {"mode": "standard", "effort": "low"},
        )

    def test_strict_json_schema_output_format_is_configured(self) -> None:
        client = self.make_client()

        self.call_service(client)

        response_format = client.responses.calls[0]["text"]["format"]
        self.assertEqual(response_format["type"], "json_schema")
        self.assertEqual(response_format["name"], "ai_creator_report")
        self.assertIs(response_format["strict"], True)

    def test_request_schema_matches_report_contract(self) -> None:
        client = self.make_client()

        self.call_service(client)

        self.assertEqual(
            client.responses.calls[0]["text"]["format"]["schema"],
            get_ai_creator_report_json_schema(),
        )

    def test_context_json_is_deterministic_and_preserves_unicode(self) -> None:
        context = {
            "z_key": "Türkçe şarkı",
            "a_key": {"views": 300},
        }
        client = self.make_client()

        self.call_service(client, context=context, language="tr")

        expected_json = json.dumps(
            context,
            ensure_ascii=False,
            sort_keys=True,
            allow_nan=False,
        )
        user_message = client.responses.calls[0]["input"]
        self.assertTrue(user_message.endswith(expected_json))
        self.assertIn("Türkçe şarkı", user_message)
        self.assertNotIn("\\u", user_message)

    def test_context_is_not_mutated(self) -> None:
        context = {"nested": {"values": [3, 1, 2]}}
        original = copy.deepcopy(context)
        client = self.make_client()

        self.call_service(client, context=context)

        self.assertEqual(context, original)

    def test_missing_api_key_is_rejected_before_client_call(self) -> None:
        client = self.make_client()

        with self.assertRaisesRegex(
            AICreatorConfigurationError,
            "^ai_service.api_key: missing$",
        ):
            self.call_service(client, api_key="  ")

        self.assertEqual(client.responses.calls, [])

    def test_invalid_language_is_rejected_before_client_call(self) -> None:
        client = self.make_client()

        with self.assertRaisesRegex(
            AICreatorConfigurationError,
            "^ai_service.language: invalid_value$",
        ):
            self.call_service(client, language="de")

        self.assertEqual(client.responses.calls, [])

    def test_invalid_context_type_is_rejected(self) -> None:
        client = self.make_client()

        with self.assertRaisesRegex(
            AICreatorConfigurationError,
            "^ai_service.context: invalid_type$",
        ):
            generate_ai_creator_report(
                context=[],
                language="en",
                api_key=self.api_key,
                client=client,
            )

        self.assertEqual(client.responses.calls, [])

    def test_empty_model_is_rejected_before_client_call(self) -> None:
        client = self.make_client()

        with self.assertRaisesRegex(
            AICreatorConfigurationError,
            "^ai_service.model: missing$",
        ):
            self.call_service(client, model=" ")

        self.assertEqual(client.responses.calls, [])

    def test_non_serializable_context_is_rejected_before_client_call(self) -> None:
        client = self.make_client()

        with self.assertRaisesRegex(
            AICreatorConfigurationError,
            "^ai_service.context: not_serializable$",
        ):
            self.call_service(client, context={"value": object()})

        self.assertEqual(client.responses.calls, [])

    def test_empty_output_text_is_rejected(self) -> None:
        client = FakeClient(FakeResponse("  "))

        with self.assertRaisesRegex(
            AICreatorResponseError,
            "^ai_service.response: empty_output$",
        ):
            self.call_service(client)

    def test_missing_output_text_is_rejected(self) -> None:
        client = FakeClient(object())

        with self.assertRaisesRegex(
            AICreatorResponseError,
            "^ai_service.response: empty_output$",
        ):
            self.call_service(client)

    def test_invalid_json_is_rejected(self) -> None:
        client = FakeClient(FakeResponse("not-json"))

        with self.assertRaisesRegex(
            AICreatorResponseError,
            "^ai_service.response: invalid_json$",
        ):
            self.call_service(client)

    def test_contract_invalid_json_is_rejected(self) -> None:
        client = FakeClient(FakeResponse('{"schema_version": "1.0"}'))

        with self.assertRaisesRegex(
            AICreatorResponseError,
            "^ai_service.response: contract_validation_failed$",
        ):
            self.call_service(client)

    def test_client_exception_is_wrapped_as_service_error(self) -> None:
        client = FakeClient(error=RuntimeError("client failed"))

        with self.assertRaisesRegex(
            AICreatorServiceError,
            "^ai_service.request: failed$",
        ) as raised:
            self.call_service(client)

        self.assertIsInstance(raised.exception.__cause__, RuntimeError)

    def test_error_messages_do_not_expose_api_key(self) -> None:
        client = FakeClient(error=RuntimeError(f"failed with {self.api_key}"))

        with self.assertRaises(AICreatorServiceError) as raised:
            self.call_service(client)

        self.assertNotIn(self.api_key, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
