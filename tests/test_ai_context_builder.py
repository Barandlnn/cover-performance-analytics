import json
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.ai_context_builder import build_ai_creator_context


class BuildAiCreatorContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cover_data = pd.DataFrame(
            [
                {
                    "cover_id": "C003",
                    "title": "Third",
                    "artist": "Artist C",
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "genre": "Pop",
                    "recording_type": "Studio",
                    "arrangement_type": "Acoustic",
                    "hook_type": "direct chorus",
                    "vocal_style": "powerful",
                    "views": 900,
                    "likes": 90,
                    "comments": 9,
                    "saves": 18,
                    "shares": 9,
                    "engagement_rate": 14.0,
                    "save_rate": 2.0,
                    "share_rate": 1.0,
                    "comment_rate": 1.0,
                    "performance_score": 105.0,
                },
                {
                    "cover_id": "C001",
                    "title": "First",
                    "artist": "Artist A",
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "genre": "Pop",
                    "recording_type": "Studio",
                    "arrangement_type": "Acoustic",
                    "hook_type": "direct chorus",
                    "vocal_style": "powerful",
                    "views": 1200,
                    "likes": 120,
                    "comments": 12,
                    "saves": 30,
                    "shares": 18,
                    "engagement_rate": 15.0,
                    "save_rate": 2.5,
                    "share_rate": 1.5,
                    "comment_rate": 1.0,
                    "performance_score": 120.0,
                },
                {
                    "cover_id": "C002",
                    "title": "Second",
                    "artist": "Artist B",
                    "platform": "TikTok",
                    "content_type": "Reel",
                    "genre": "Rock",
                    "recording_type": "Live",
                    "arrangement_type": "Full band",
                    "hook_type": "slow intro",
                    "vocal_style": "emotional",
                    "views": 1100,
                    "likes": 100,
                    "comments": 10,
                    "saves": 22,
                    "shares": 11,
                    "engagement_rate": 13.0,
                    "save_rate": 2.0,
                    "share_rate": 1.0,
                    "comment_rate": 0.9,
                    "performance_score": 120.0,
                },
                {
                    "cover_id": "C004",
                    "title": "Fourth",
                    "artist": "Artist D",
                    "platform": "TikTok",
                    "content_type": "Short",
                    "genre": "Rock",
                    "recording_type": "Live",
                    "arrangement_type": "Full band",
                    "hook_type": "slow intro",
                    "vocal_style": "emotional",
                    "views": 700,
                    "likes": 70,
                    "comments": 7,
                    "saves": 14,
                    "shares": 7,
                    "engagement_rate": 14.0,
                    "save_rate": 2.0,
                    "share_rate": 1.0,
                    "comment_rate": 1.0,
                    "performance_score": 90.0,
                },
                {
                    "cover_id": "C005",
                    "title": "Fifth",
                    "artist": "Artist E",
                    "platform": "YouTube",
                    "content_type": "Short",
                    "genre": "Jazz",
                    "recording_type": "Home",
                    "arrangement_type": "Piano",
                    "hook_type": "verse",
                    "vocal_style": "soft",
                    "views": 500,
                    "likes": 40,
                    "comments": 5,
                    "saves": 8,
                    "shares": 4,
                    "engagement_rate": 11.4,
                    "save_rate": 1.6,
                    "share_rate": 0.8,
                    "comment_rate": 1.0,
                    "performance_score": 70.0,
                },
            ]
        )

    def test_representative_dataframe_produces_required_structure(self) -> None:
        context = build_ai_creator_context(self.cover_data)

        self.assertEqual(
            set(context),
            {
                "context_version",
                "data_summary",
                "portfolio_metrics",
                "top_covers",
                "group_performance",
                "data_quality",
            },
        )
        self.assertEqual(context["context_version"], "1.0")
        self.assertEqual(context["data_summary"]["cover_count"], 5)
        self.assertEqual(context["data_summary"]["platform_count"], 3)
        self.assertEqual(context["data_summary"]["genre_count"], 3)
        self.assertEqual(context["data_summary"]["content_type_count"], 2)
        self.assertEqual(context["portfolio_metrics"]["total_views"], 4400)
        self.assertIn("average_performance_score", context["portfolio_metrics"])
        self.assertEqual(context["portfolio_metrics"]["median_views"], 900)
        self.assertEqual(
            context["portfolio_metrics"]["median_performance_score"],
            105,
        )
        self.assertTrue(
            all(
                cover["evidence_quality"] == "standard"
                and cover["evidence_flags"] == []
                for cover in context["top_covers"]
            )
        )
        self.assertTrue(context["data_quality"]["is_sufficient"])

    def test_top_covers_are_sorted_deterministically(self) -> None:
        context = build_ai_creator_context(self.cover_data, top_n=3)

        self.assertEqual(
            [cover["cover_id"] for cover in context["top_covers"]],
            ["C001", "C002", "C003"],
        )

    def test_empty_dataframe_returns_valid_insufficient_context(self) -> None:
        context = build_ai_creator_context(pd.DataFrame())

        self.assertEqual(context["data_summary"], {"cover_count": 0})
        self.assertEqual(context["portfolio_metrics"], {})
        self.assertEqual(context["top_covers"], [])
        self.assertEqual(context["group_performance"], {})
        self.assertFalse(context["data_quality"]["is_sufficient"])
        self.assertIn("empty_dataset", context["data_quality"]["limitations"])
        self.assertIn(
            "insufficient_cover_count",
            context["data_quality"]["limitations"],
        )

    def test_missing_optional_columns_use_deterministic_metric_fallback(self) -> None:
        minimal_data = pd.DataFrame(
            {
                "cover_id": ["C001", "C002", "C003"],
                "title": ["First", "Second", "Third"],
                "views": [100, 300, 200],
            }
        )

        context = build_ai_creator_context(minimal_data)

        self.assertEqual(
            [cover["cover_id"] for cover in context["top_covers"]],
            ["C002", "C003", "C001"],
        )
        self.assertTrue(context["data_quality"]["is_sufficient"])
        self.assertIn(
            "missing_performance_score",
            context["data_quality"]["limitations"],
        )
        self.assertIn(
            "performance_score",
            context["data_quality"]["missing_columns"],
        )

    def test_input_dataframe_is_not_mutated(self) -> None:
        original = self.cover_data.copy(deep=True)

        build_ai_creator_context(self.cover_data)

        assert_frame_equal(self.cover_data, original)

    def test_nan_and_infinity_are_removed_from_context(self) -> None:
        invalid_data = self.cover_data.copy(deep=True)
        invalid_data["views"] = invalid_data["views"].astype(float)
        invalid_data.loc[0, "performance_score"] = float("inf")
        invalid_data.loc[1, "engagement_rate"] = float("nan")
        invalid_data.loc[2, "views"] = float("-inf")
        invalid_data.loc[3, "title"] = float("nan")

        context = build_ai_creator_context(invalid_data)

        serialized = json.dumps(context, allow_nan=False)
        self.assertIsInstance(serialized, str)

    def test_groups_below_minimum_size_are_excluded(self) -> None:
        context = build_ai_creator_context(self.cover_data, min_group_size=2)

        genre_groups = context["group_performance"]["genre"]
        self.assertEqual(
            [group["value"] for group in genre_groups],
            ["Pop", "Rock"],
        )
        self.assertNotIn("Jazz", [group["value"] for group in genre_groups])

    def test_high_score_low_view_cover_is_flagged_as_low_quality(self) -> None:
        data = pd.DataFrame(
            {
                "cover_id": ["LOW", "NORMAL-1", "NORMAL-2"],
                "views": [50, 1000, 1200],
                "performance_score": [1000.0, 200.0, 100.0],
            }
        )

        context = build_ai_creator_context(data)
        covers = {
            cover["cover_id"]: cover
            for cover in context["top_covers"]
        }

        self.assertEqual(covers["LOW"]["evidence_quality"], "low")
        self.assertIn("low_view_sample", covers["LOW"]["evidence_flags"])
        self.assertEqual(covers["NORMAL-1"]["evidence_quality"], "standard")
        self.assertEqual(covers["NORMAL-1"]["evidence_flags"], [])
        self.assertEqual(covers["NORMAL-2"]["evidence_quality"], "standard")
        self.assertIn(
            "low_view_rate_outlier",
            context["data_quality"]["limitations"],
        )

    def test_portfolio_medians_are_calculated_from_finite_values(self) -> None:
        data = pd.DataFrame(
            {
                "cover_id": ["C001", "C002", "C003", "C004"],
                "views": [100, 300, 500, float("inf")],
                "performance_score": [10, 30, 50, float("nan")],
            }
        )

        context = build_ai_creator_context(data)

        self.assertEqual(context["portfolio_metrics"]["median_views"], 300)
        self.assertEqual(
            context["portfolio_metrics"]["median_performance_score"],
            30,
        )

    def test_fewer_than_three_positive_views_do_not_trigger_low_view_flag(self) -> None:
        data = pd.DataFrame(
            {
                "cover_id": ["LOW", "NORMAL", "ZERO"],
                "views": [50, 1000, 0],
                "performance_score": [1000.0, 200.0, 100.0],
            }
        )

        context = build_ai_creator_context(data)

        self.assertTrue(
            all(
                cover["evidence_quality"] == "standard"
                and cover["evidence_flags"] == []
                for cover in context["top_covers"]
            )
        )
        self.assertNotIn(
            "low_view_rate_outlier",
            context["data_quality"]["limitations"],
        )


if __name__ == "__main__":
    unittest.main()
