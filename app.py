import pandas as pd
import streamlit as st
from datetime import datetime
import os

try:
    from src.pattern_analyzer import (
        get_all_pattern_summaries,
        generate_pattern_insights,
        generate_pattern_recommendations,
        score_cover_candidate,
        generate_candidate_explanations,
    )
except Exception:
    from pattern_analyzer import (
        get_all_pattern_summaries,
        generate_pattern_insights,
        generate_pattern_recommendations,
        score_cover_candidate,
        generate_candidate_explanations,
    )

from src.analyzer import (
    load_data,
    calculate_metrics,
    get_top_covers,
    generate_insights,
    calculate_growth_metrics,
    get_growth_summary,
    get_cover_snapshot_history,
)

DATA_PATH = "data/covers.csv"
SNAPSHOTS_PATH = "data/metrics_snapshots.csv"
CANDIDATE_TESTS_PATH = "data/candidate_tests.csv"

def save_candidate_test_result(
    file_path: str,
    genre: str,
    artist: str,
    content_type: str,
    candidate_summary: dict,
) -> None:
    """
    Candidate test sonucunu CSV dosyasına kaydeder.
    """

    new_record = {
        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "genre": genre,
        "artist": artist,
        "content_type": content_type,
        "candidate_score": candidate_summary["candidate_score"],
        "candidate_label": candidate_summary["candidate_label"],
        "needs_more_data_count": candidate_summary["needs_more_data_count"],
        "action": candidate_summary["action"],
    }

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    new_df = pd.DataFrame([new_record])

    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_csv(file_path, index=False)


st.set_page_config(page_title="Cover Performance Analytics", layout="wide")

st.title("Cover Performance Analytics")
st.write("Analyze your cover performances across platforms.")


# -----------------------------
# LOAD RAW DATA
# -----------------------------

raw_df = load_data(DATA_PATH)

covers_df = pd.read_csv(DATA_PATH)
snapshots_df = pd.read_csv(SNAPSHOTS_PATH)


# -----------------------------
# ADD NEW COVER FORM
# -----------------------------

st.sidebar.header("Add New Cover")

with st.sidebar.form("add_cover_form", clear_on_submit=True):
    title = st.text_input("Cover Title")
    artist = st.text_input("Original Artist")

    platform = st.selectbox("Platform", ["Instagram", "YouTube", "TikTok"])

    content_type = st.selectbox(
        "Content Type", ["Reels", "Shorts", "TikTok Video", "Post"]
    )

    genre = st.text_input("Genre", placeholder="Example: Rock Acoustic")

    post_date = st.date_input("Post Date")

    views = st.number_input("Views", min_value=1, step=100)
    likes = st.number_input("Likes", min_value=0, step=10)
    comments = st.number_input("Comments", min_value=0, step=1)
    saves = st.number_input("Saves", min_value=0, step=1)
    shares = st.number_input("Shares", min_value=0, step=1)

    duration_sec = st.number_input("Duration Seconds", min_value=1, step=1)

    hook_type = st.selectbox(
        "Hook Type",
        ["direct chorus", "slow intro", "instrumental intro", "vocal intro", "other"],
    )

    vocal_style = st.selectbox(
        "Vocal Style", ["soft", "powerful", "emotional", "mixed", "other"]
    )

    language = st.selectbox("Language", ["Turkish", "English", "Other"])
    post_time = st.time_input("Post Time")

    caption_text = st.text_area(
        "Caption Text",
        placeholder="Paste or write the caption here",
    )

    hashtags = st.text_input(
        "Hashtags",
        placeholder="#cover #music #acoustic",
    )

    audio_quality_score = st.slider(
        "Audio Quality Score",
        min_value=1,
        max_value=5,
        value=3,
    )

    thumbnail_score = st.slider(
        "Thumbnail Score",
        min_value=1,
        max_value=5,
        value=3,
    )

    recording_type = st.selectbox(
        "Recording Type",
        ["home", "studio", "live", "other"],
    )

    arrangement_type = st.selectbox(
        "Arrangement Type",
        ["acoustic", "piano", "full band", "guitar vocal", "other"],
    )

    song_mood = st.selectbox(
        "Song Mood",
        ["emotional", "energetic", "melancholic", "romantic", "dark", "other"],
    )

    content_origin = st.selectbox(
        "Content Origin",
        ["cover", "original"],
    )

    submitted = st.form_submit_button("Add Cover")

    if submitted:
        if title.strip() == "" or artist.strip() == "" or genre.strip() == "":
            st.warning("Please fill title, artist and genre fields.")
        else:
            covers_df = pd.read_csv(DATA_PATH)
            snapshots_df = pd.read_csv(SNAPSHOTS_PATH)

            # New cover_id üret
            if covers_df.empty:
                new_cover_id = "C001"
            else:
                last_cover_number = (
                    covers_df["cover_id"]
                    .str.replace("C", "", regex=False)
                    .astype(int)
                    .max()
                )
                new_cover_id = f"C{last_cover_number + 1:03d}"

            # New snapshot_id üret
            if snapshots_df.empty:
                new_snapshot_id = "S001"
            else:
                last_snapshot_number = (
                    snapshots_df["snapshot_id"]
                    .str.replace("S", "", regex=False)
                    .astype(int)
                    .max()
                )
                new_snapshot_id = f"S{last_snapshot_number + 1:03d}"
            clean_hashtags = hashtags.strip()

            hashtag_count = len(
                [tag for tag in clean_hashtags.replace(",", " ").split() if tag.strip()]
            )

            new_cover = {
                "cover_id": new_cover_id,
                "title": title,
                "artist": artist,
                "platform": platform,
                "content_type": content_type,
                "genre": genre,
                "post_date": str(post_date),
                "duration_sec": duration_sec,
                "hook_type": hook_type,
                "vocal_style": vocal_style,
                "language": language,
                "post_time": post_time.strftime("%H:%M"),
                "caption_length": len(caption_text),
                "hashtags": clean_hashtags,
                "hashtag_count": hashtag_count,
                "audio_quality_score": audio_quality_score,
                "thumbnail_score": thumbnail_score,
                "recording_type": recording_type,
                "arrangement_type": arrangement_type,
                "song_mood": song_mood,
                "content_origin": content_origin,
            }

            new_snapshot = {
                "snapshot_id": new_snapshot_id,
                "cover_id": new_cover_id,
                "snapshot_date": pd.Timestamp.today().date().isoformat(),
                "views": views,
                "likes": likes,
                "comments": comments,
                "saves": saves,
                "shares": shares,
            }

            updated_covers_df = pd.concat(
                [covers_df, pd.DataFrame([new_cover])],
                ignore_index=True,
            )

            updated_snapshots_df = pd.concat(
                [snapshots_df, pd.DataFrame([new_snapshot])],
                ignore_index=True,
            )

            updated_covers_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
            updated_snapshots_df.to_csv(
                SNAPSHOTS_PATH,
                index=False,
                encoding="utf-8-sig",
            )

            st.success("Cover and first metric snapshot added successfully!")

            st.rerun()

# ------------------------
# ADD METRIC SNAPSHOT FORM
# ------------------------

st.sidebar.divider()
st.sidebar.header("Add Metric Snapshot")

covers_for_snapshot = pd.read_csv(DATA_PATH)

if covers_for_snapshot.empty:
    st.sidebar.info("No covers available for snapshot.")
else:
    covers_for_snapshot["display_name"] = (
        covers_for_snapshot["cover_id"]
        + " - "
        + covers_for_snapshot["title"]
        + " / "
        + covers_for_snapshot["artist"]
    )

    selected_cover_display = st.sidebar.selectbox(
        "Select Cover",
        covers_for_snapshot["display_name"].tolist(),
    )

    selected_cover_id = selected_cover_display.split(" - ")[0]

    snapshots_preview_df = pd.read_csv(SNAPSHOTS_PATH)

    selected_snapshots_df = snapshots_preview_df[
        snapshots_preview_df["cover_id"] == selected_cover_id
    ].copy()

    latest_snapshot = None

    if not selected_snapshots_df.empty:
        selected_snapshots_df["snapshot_date"] = pd.to_datetime(
            selected_snapshots_df["snapshot_date"],
            errors="coerce",
        )

        selected_snapshots_df = selected_snapshots_df.sort_values(
            by=["snapshot_date", "snapshot_id"]
        )

        latest_snapshot = selected_snapshots_df.iloc[-1]

        st.sidebar.caption("Latest snapshot for selected cover:")
        st.sidebar.write(f"Date: **{latest_snapshot['snapshot_date'].date()}**")
        st.sidebar.write(f"Views: **{latest_snapshot['views']}**")
        st.sidebar.write(f"Likes: **{latest_snapshot['likes']}**")
        st.sidebar.write(f"Comments: **{latest_snapshot['comments']}**")
        st.sidebar.write(f"Saves: **{latest_snapshot['saves']}**")
        st.sidebar.write(f"Shares: **{latest_snapshot['shares']}**")

    default_views = 0
    default_likes = 0
    default_comments = 0
    default_saves = 0
    default_shares = 0

    if latest_snapshot is not None:
        default_views = int(latest_snapshot["views"])
        default_likes = int(latest_snapshot["likes"])
        default_comments = int(latest_snapshot["comments"])
        default_saves = int(latest_snapshot["saves"])
        default_shares = int(latest_snapshot["shares"])

    with st.sidebar.form("add_metric_snapshot_form"):
        snapshot_date = st.date_input("Snapshot Date")

        snapshot_views = st.number_input(
            "Snapshot Views",
            min_value=0,
            value=default_views,
            step=1,
        )

        snapshot_likes = st.number_input(
            "Snapshot Likes",
            min_value=0,
            value=default_likes,
            step=1,
        )

        snapshot_comments = st.number_input(
            "Snapshot Comments",
            min_value=0,
            value=default_comments,
            step=1,
        )

        snapshot_saves = st.number_input(
            "Snapshot Saves",
            min_value=0,
            value=default_saves,
            step=1,
        )

        snapshot_shares = st.number_input(
            "Snapshot Shares",
            min_value=0,
            value=default_shares,
            step=1,
        )

        snapshot_submitted = st.form_submit_button("Add Snapshot")

        if snapshot_submitted:
            snapshots_df = pd.read_csv(SNAPSHOTS_PATH)

            has_invalid_snapshot = False

            if latest_snapshot is not None:
                if snapshot_views < latest_snapshot["views"]:
                    st.sidebar.error(
                        "New views value cannot be lower than the latest snapshot."
                    )
                    has_invalid_snapshot = True

                if snapshot_likes < latest_snapshot["likes"]:
                    st.sidebar.error(
                        "New likes value cannot be lower than the latest snapshot."
                    )
                    has_invalid_snapshot = True

                if snapshot_comments < latest_snapshot["comments"]:
                    st.sidebar.error(
                        "New comments value cannot be lower than the latest snapshot."
                    )
                    has_invalid_snapshot = True

                if snapshot_saves < latest_snapshot["saves"]:
                    st.sidebar.error(
                        "New saves value cannot be lower than the latest snapshot."
                    )
                    has_invalid_snapshot = True
                if snapshot_shares < latest_snapshot["shares"]:
                    st.sidebar.error(
                        "New shares value cannot be lower than the latest snapshot."
                    )
                    has_invalid_snapshot = True

            if has_invalid_snapshot:
                st.stop()

            if snapshots_df.empty:
                new_snapshot_id = "S001"
            else:
                last_snapshot_number = (
                    snapshots_df["snapshot_id"]
                    .str.replace("S", "", regex=False)
                    .astype(int)
                    .max()
                )
                new_snapshot_id = f"S{last_snapshot_number + 1:03d}"

            new_snapshot = {
                "snapshot_id": new_snapshot_id,
                "cover_id": selected_cover_id,
                "snapshot_date": str(snapshot_date),
                "views": snapshot_views,
                "likes": snapshot_likes,
                "comments": snapshot_comments,
                "saves": snapshot_saves,
                "shares": snapshot_shares,
            }

            views_diff = snapshot_views
            likes_diff = snapshot_likes
            comments_diff = snapshot_comments
            saves_diff = snapshot_saves
            shares_diff = snapshot_shares

            if latest_snapshot is not None:
                views_diff = snapshot_views - latest_snapshot["views"]
                likes_diff = snapshot_likes - latest_snapshot["likes"]
                comments_diff = snapshot_comments - latest_snapshot["comments"]
                saves_diff = snapshot_saves - latest_snapshot["saves"]
                shares_diff = snapshot_shares - latest_snapshot["shares"]

            st.sidebar.info(
                f"Snapshot difference → "
                f"Views: {views_diff}, "
                f"Likes: {likes_diff}, "
                f"Comments: {comments_diff}, "
                f"Saves: {saves_diff}, "
                f"Shares: {shares_diff}"
            )

            updated_snapshots_df = pd.concat(
                [snapshots_df, pd.DataFrame([new_snapshot])],
                ignore_index=True,
            )

            updated_snapshots_df.to_csv(
                SNAPSHOTS_PATH,
                index=False,
                encoding="utf-8-sig",
            )

            st.success("Metric snapshot added successfully!")

            st.rerun()

# -----------------------------
# CALCULATE METRICS
# -----------------------------

df = calculate_metrics(raw_df)


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("Filters")

platform_options = ["All"] + sorted(df["platform"].unique().tolist())
selected_platform = st.sidebar.selectbox("Platform Filter", platform_options)

genre_options = ["All"] + sorted(df["genre"].unique().tolist())
selected_genre = st.sidebar.selectbox("Genre Filter", genre_options)

filtered_df = df.copy()

if selected_platform != "All":
    filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["genre"] == selected_genre]


# -----------------------------
# EMPTY FILTER CHECK
# -----------------------------

if filtered_df.empty:
    st.warning("No covers found for the selected filters.")
    st.stop()


# -----------------------------
# KPI CARDS
# -----------------------------

st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

total_covers = len(filtered_df)
average_engagement = filtered_df["engagement_rate"].mean()
average_save_rate = filtered_df["save_rate"].mean()
best_score = filtered_df["performance_score"].max()

col1.metric("Total Covers", total_covers)
col2.metric("Avg Engagement Rate", f"{average_engagement:.2f}%")
col3.metric("Avg Save Rate", f"{average_save_rate:.2f}%")
col4.metric("Best Score", f"{best_score:.2f}")


# -----------------------------
# ALL COVERS TABLE
# -----------------------------

st.subheader("All Covers")

st.dataframe(
    filtered_df[
        [
            "cover_id",
            "snapshot_id",
            "snapshot_date",
            "title",
            "artist",
            "platform",
            "content_type",
            "genre",
            "post_date",
            "post_time",
            "duration_sec",
            "hook_type",
            "vocal_style",
            "language",
            "caption_length",
            "hashtags",
            "hashtag_count",
            "audio_quality_score",
            "thumbnail_score",
            "recording_type",
            "arrangement_type",
            "song_mood",
            "content_origin",
            "views",
            "likes",
            "comments",
            "saves",
            "shares",
            "engagement_rate",
            "save_rate",
            "share_rate",
            "comment_rate",
            "performance_score",
        ]
    ],
    hide_index=True,
    use_container_width=True,
)


# -----------------------------
# TOP COVERS
# -----------------------------

st.subheader("Top Performing Covers")

top_covers = get_top_covers(filtered_df)

st.dataframe(
    top_covers[
        [
            "cover_id",
            "snapshot_id",
            "snapshot_date",
            "title",
            "artist",
            "platform",
            "genre",
            "post_time",
            "duration_sec",
            "hook_type",
            "vocal_style",
            "audio_quality_score",
            "thumbnail_score",
            "recording_type",
            "arrangement_type",
            "song_mood",
            "content_origin",
            "views",
            "likes",
            "comments",
            "saves",
            "shares",
            "engagement_rate",
            "save_rate",
            "share_rate",
            "comment_rate",
            "performance_score",
        ]
    ],
    hide_index=True,
    use_container_width=True,
)


# -----------------------------
# BAR CHART
# -----------------------------

st.subheader("Performance Score Chart")

chart_data = filtered_df.set_index("title")["performance_score"]

st.bar_chart(chart_data)


# -----------------------------
# QUICK INSIGHTS
# -----------------------------

st.subheader("Quick Insights")

best_cover = top_covers.iloc[0]

st.success(f"Best performing cover: {best_cover['title']}")

st.write(f"Artist: **{best_cover['artist']}**")
st.write(f"Genre: **{best_cover['genre']}**")
st.write(f"Hook type: **{best_cover['hook_type']}**")
st.write(f"Vocal style: **{best_cover['vocal_style']}**")
st.write(f"Performance score: **{best_cover['performance_score']}**")
st.write(f"Engagement rate: **{best_cover['engagement_rate']}%**")
st.write(f"Save rate: **{best_cover['save_rate']}%**")
st.write(f"Share rate: **{best_cover['share_rate']}%**")

st.info(
    "This result suggests that this type of cover may match your audience better. "
    "To make stronger conclusions, add more real cover data."
)

st.subheader("AI-Like Interpretation")

insights = generate_insights(filtered_df, best_cover)

for insight in insights:
    st.write(f"- {insight}")

# -------------------------------
# V1.6 - GROWTH ANALYTICS
# -------------------------------

st.markdown("---")
st.header("📈 Growth Analytics")
st.caption("Cover'ların zaman içindeki performans gelişimini analiz eder.")

try:
    growth_summary = get_growth_summary(covers_df, snapshots_df)

    if growth_summary.empty:
        st.info(
            "Growth analizi için henüz yeterli snapshot verisi yok. "
            "Bir cover için en az 2 snapshot gerekli."
        )
    else:
        st.subheader("🚀 Growth Summary")

        best_views_growth = growth_summary.sort_values(
            by="views_growth",
            ascending=False,
        ).iloc[0]

        best_likes_growth = growth_summary.sort_values(
            by="likes_growth",
            ascending=False,
        ).iloc[0]

        best_engagement_growth = growth_summary.sort_values(
            by="total_engagement_growth",
            ascending=False,
        ).iloc[0]

        growth_col1, growth_col2, growth_col3 = st.columns(3)

        growth_col1.metric(
            "Best Views Growth",
            best_views_growth["title"],
            int(best_views_growth["views_growth"]),
        )

        growth_col2.metric(
            "Best Likes Growth",
            best_likes_growth["title"],
            int(best_likes_growth["likes_growth"]),
        )

        growth_col3.metric(
            "Best Engagement Growth",
            best_engagement_growth["title"],
            int(best_engagement_growth["total_engagement_growth"]),
        )

        preferred_columns = [
            "cover_id",
            "title",
            "artist",
            "platform",
            "genre",
            "snapshot_count",
            "first_snapshot_date",
            "latest_snapshot_date",
            "views_growth",
            "likes_growth",
            "comments_growth",
            "saves_growth",
            "shares_growth",
            "total_engagement_growth",
            "views_growth_rate",
            "likes_growth_rate",
        ]

        available_columns = [
            column for column in preferred_columns if column in growth_summary.columns
        ]

        if available_columns:
            st.dataframe(
                growth_summary[available_columns],
                use_container_width=True,
            )
        else:
            st.dataframe(growth_summary, use_container_width=True)

        with st.expander("Debug: Growth Summary Columns"):
            st.write(list(growth_summary.columns))

    st.markdown("---")
    st.subheader("📊 Selected Cover Snapshot History")

    growth_cover_options_df = covers_df.copy()

    if growth_cover_options_df.empty:
        st.info("Snapshot geçmişi göstermek için önce en az bir cover eklemelisin.")
    else:
        growth_cover_options_df["display_name"] = (
            growth_cover_options_df["cover_id"]
            + " - "
            + growth_cover_options_df["title"]
            + " / "
            + growth_cover_options_df["artist"]
        )

        selected_growth_cover_display = st.selectbox(
            "Select a cover to inspect snapshot history",
            growth_cover_options_df["display_name"].tolist(),
            key="growth_cover_selector",
        )

        selected_growth_cover_id = selected_growth_cover_display.split(" - ")[0]

        cover_history = get_cover_snapshot_history(
            snapshots_df=snapshots_df,
            cover_id=selected_growth_cover_id,
        )

        if cover_history.empty:
            st.info("Bu cover için henüz snapshot geçmişi bulunamadı.")
        else:
            preferred_history_columns = [
                "snapshot_id",
                "snapshot_date",
                "views",
                "likes",
                "comments",
                "saves",
                "shares",
                "total_engagement",
                "engagement_rate",
            ]

            available_history_columns = [
                column
                for column in preferred_history_columns
                if column in cover_history.columns
            ]

            st.dataframe(
                cover_history[available_history_columns],
                hide_index=True,
                use_container_width=True,
            )

            chart_history = cover_history.copy()
            chart_history["snapshot_date"] = pd.to_datetime(
                chart_history["snapshot_date"],
                errors="coerce",
            )
            chart_history = chart_history.dropna(subset=["snapshot_date"])
            chart_history = chart_history.set_index("snapshot_date")

            if not chart_history.empty:
                st.subheader("📈 Views Trend")
                st.line_chart(chart_history[["views"]])

                engagement_columns = [
                    column
                    for column in [
                        "likes",
                        "comments",
                        "saves",
                        "shares",
                        "total_engagement",
                    ]
                    if column in chart_history.columns
                ]

                if engagement_columns:
                    st.subheader("❤️ Engagement Trend")
                    st.line_chart(chart_history[engagement_columns])

except FileNotFoundError:
    st.warning(
        "metrics_snapshots.csv dosyası bulunamadı. "
        "Önce en az bir metric snapshot eklemelisin."
    )

except Exception as error:
    st.error(f"Growth Analytics yüklenirken bir hata oluştu: {error}")


# -------------------------------
# V2 - PATTERN ANALYTICS
# -------------------------------

st.markdown("---")
st.header("📊 V2 Pattern Analytics")
st.caption(
    "Analyze which genres, artists, and content types perform better based on "
    "latest metrics and growth data."
)

try:
    covers_df_v2 = pd.read_csv(DATA_PATH)
    snapshots_df_v2 = pd.read_csv(SNAPSHOTS_PATH)

    pattern_summaries = get_all_pattern_summaries(
        covers_df_v2,
        snapshots_df_v2,
    )

    if not pattern_summaries:
        st.info("Pattern analytics is not available yet. Required columns may be missing.")
    else:
        pattern_insights = generate_pattern_insights(pattern_summaries)
        pattern_recommendations = generate_pattern_recommendations(pattern_summaries)

        st.subheader("🧠 V2 Pattern Insights")

        for insight in pattern_insights:
            st.info(insight)

        st.subheader("🎯 V2 Cover Planning Recommendations")

        if pattern_recommendations.empty:
            st.info("No planning recommendations are available yet.")
        else:
            st.dataframe(
                pattern_recommendations,
                use_container_width=True,
            )

            top_recommendation = pattern_recommendations.iloc[0]

            st.success(
                f"Top recommendation: {top_recommendation['pattern']} "
                f"({top_recommendation['dimension']}) — "
                f"{top_recommendation['priority']}. "
                f"{top_recommendation['action']}"
            )

        st.subheader("🧪 V2 Next Cover Candidate Test")
        st.caption(
            "Select a possible future cover profile and estimate how strong it looks "
            "based on current pattern data."
        )

        def _get_candidate_options(dimension: str) -> list[str]:
            summary_df = pattern_summaries.get(dimension)

            if (
                summary_df is None
                or summary_df.empty
                or dimension not in summary_df.columns
            ):
                return ["Not available"]

            return summary_df[dimension].astype(str).tolist()

        candidate_col1, candidate_col2, candidate_col3 = st.columns(3)

        with candidate_col1:
            selected_candidate_genre = st.selectbox(
                "Candidate Genre",
                _get_candidate_options("genre"),
                key="candidate_genre_selector",
            )

        with candidate_col2:
            selected_candidate_artist = st.selectbox(
                "Candidate Artist",
                _get_candidate_options("artist"),
                key="candidate_artist_selector",
            )

        with candidate_col3:
            selected_candidate_content_type = st.selectbox(
                "Candidate Content Type",
                _get_candidate_options("content_type"),
                key="candidate_content_type_selector",
            )

        if st.button("Analyze Candidate Cover", key="analyze_candidate_button"):
            candidate_details_df, candidate_summary = score_cover_candidate(
                pattern_summaries,
                {
                    "genre": selected_candidate_genre,
                    "artist": selected_candidate_artist,
                    "content_type": selected_candidate_content_type,
                },
            )

            st.session_state["last_candidate_test"] = {
                "genre": selected_candidate_genre,
                "artist": selected_candidate_artist,
                "content_type": selected_candidate_content_type,
                "details_df": candidate_details_df,
                "summary": candidate_summary,
            }

        last_candidate_test = st.session_state.get("last_candidate_test")

        if last_candidate_test is not None:
            candidate_details_df = last_candidate_test["details_df"]
            candidate_summary = last_candidate_test["summary"]

            st.metric(
                "Candidate Score",
                candidate_summary["candidate_score"],
                candidate_summary["candidate_label"],
            )

            if candidate_summary["candidate_label"] in [
                "Strong Candidate",
                "Promising Candidate",
            ]:
                st.success(candidate_summary["action"])
            elif candidate_summary["candidate_label"] == "Interesting but Needs More Data":
                st.warning(candidate_summary["action"])
            else:
                st.info(candidate_summary["action"])

            candidate_explanations = generate_candidate_explanations(
                candidate_details_df,
                candidate_summary,
            )

            st.subheader("🧠 Candidate Explanation")

            for explanation in candidate_explanations:
                st.info(explanation)

            st.dataframe(
                candidate_details_df,
                use_container_width=True,
            )

            if st.button("Save Candidate Test Result", key="save_candidate_button"):
                save_candidate_test_result(
                    CANDIDATE_TESTS_PATH,
                    last_candidate_test["genre"],
                    last_candidate_test["artist"],
                    last_candidate_test["content_type"],
                    last_candidate_test["summary"],
                )

                st.success("Candidate test result saved successfully.")

        st.subheader("📜 Candidate Test History")

        if os.path.exists(CANDIDATE_TESTS_PATH):
            candidate_history_df = pd.read_csv(CANDIDATE_TESTS_PATH)

            if candidate_history_df.empty:
                st.info("No candidate test history yet.")
            else:
                st.dataframe(
                    candidate_history_df.sort_values(
                        "test_date",
                        ascending=False,
                    ),
                    use_container_width=True,
                )
        else:
            st.info("No candidate test history yet.")

        dimension_labels = {
            "genre": "🎵 Genre Performance",
            "artist": "🎤 Artist Performance",
            "content_type": "🎬 Content Type Performance",
        }

        available_dimensions = list(pattern_summaries.keys())

        tabs = st.tabs(
            [
                dimension_labels.get(dimension, dimension.title())
                for dimension in available_dimensions
            ]
        )

        for tab, dimension in zip(tabs, available_dimensions):
            with tab:
                summary_df = pattern_summaries[dimension]

                if summary_df.empty:
                    st.warning(f"No data available for {dimension}.")
                    continue

                st.subheader(dimension_labels.get(dimension, dimension.title()))

                st.dataframe(
                    summary_df,
                    use_container_width=True,
                )

                chart_df = summary_df.set_index(dimension)

                st.bar_chart(chart_df["weighted_pattern_score"])

                best_row = summary_df.iloc[0]

                st.success(
                    f"Best weighted {dimension}: "
                    f"{best_row[dimension]} "
                    f"with weighted pattern score "
                    f"{best_row['weighted_pattern_score']} "
                    f"({best_row['decision_label']})"
                )

except Exception as error:
    st.error("V2 Pattern Analytics could not be loaded.")
    st.exception(error)
