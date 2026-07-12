import pandas as pd
import streamlit as st

from src.i18n import t

from src.data_manager import (
    load_covers_raw,
    load_snapshots_raw,
    append_new_cover,
    append_metric_snapshot,
)


def _generate_next_id(
    df: pd.DataFrame,
    id_column: str,
    prefix: str,
) -> str:
    """
    Return the next available ID for the given DataFrame column and prefix.

    Examples:
    C001, C002, C003...
    S001, S002, S003...
    """
    if df.empty or id_column not in df.columns:
        return f"{prefix}001"

    numeric_values = df[id_column].astype(str).str.replace(prefix, "", regex=False)

    numeric_values = pd.to_numeric(
        numeric_values,
        errors="coerce",
    )

    if numeric_values.dropna().empty:
        return f"{prefix}001"

    last_number = int(numeric_values.max())

    return f"{prefix}{last_number + 1:03d}"


def _calculate_hashtag_count(hashtags: str) -> int:
    """
    Return the number of hashtags entered for a cover.

    Both comma-separated and space-separated hashtag text are supported.
    """
    clean_hashtags = hashtags.strip()

    return len([tag for tag in clean_hashtags.replace(",", " ").split() if tag.strip()])


def _get_latest_snapshot(
    snapshots_df: pd.DataFrame,
    selected_cover_id: str,
):
    """
    Return the latest metric snapshot for the selected cover.

    Return None when the selected cover has no metric snapshots.
    """
    selected_snapshots_df = snapshots_df[
        snapshots_df["cover_id"] == selected_cover_id
    ].copy()

    if selected_snapshots_df.empty:
        return None

    selected_snapshots_df["snapshot_date"] = pd.to_datetime(
        selected_snapshots_df["snapshot_date"],
        errors="coerce",
    )

    selected_snapshots_df = selected_snapshots_df.sort_values(
        by=["snapshot_date", "snapshot_id"]
    )

    return selected_snapshots_df.iloc[-1]


def _render_latest_snapshot_preview(
    latest_snapshot,
    language: str,
) -> None:
    """
    Render a compact preview of the latest metrics for the selected cover.
    """
    if latest_snapshot is None:
        return

    latest_snapshot_date = latest_snapshot["snapshot_date"]

    if pd.notna(latest_snapshot_date):
        latest_snapshot_date_text = latest_snapshot_date.date()
    else:
        latest_snapshot_date_text = t(
            "sidebar.snapshot.unknown_date",
            language,
        )

    st.sidebar.caption(t("sidebar.snapshot.latest_preview", language))

    st.sidebar.write(
        f"{t('sidebar.snapshot.date', language)}: " f"**{latest_snapshot_date_text}**"
    )

    st.sidebar.write(
        f"{t('sidebar.snapshot.views', language)}: " f"**{latest_snapshot['views']}**"
    )

    st.sidebar.write(
        f"{t('sidebar.snapshot.likes', language)}: " f"**{latest_snapshot['likes']}**"
    )

    st.sidebar.write(
        f"{t('sidebar.snapshot.comments', language)}: "
        f"**{latest_snapshot['comments']}**"
    )

    st.sidebar.write(
        f"{t('sidebar.snapshot.saves', language)}: " f"**{latest_snapshot['saves']}**"
    )

    st.sidebar.write(
        f"{t('sidebar.snapshot.shares', language)}: " f"**{latest_snapshot['shares']}**"
    )


def _validate_new_snapshot_values(
    latest_snapshot,
    snapshot_views: int,
    snapshot_likes: int,
    snapshot_comments: int,
    snapshot_saves: int,
    snapshot_shares: int,
    language: str,
) -> bool:
    """
    Validate that new metric values are not lower than the latest recorded values.

    Return True when all values are valid.
    Return False when at least one value is invalid.
    """
    if latest_snapshot is None:
        return True

    has_invalid_snapshot = False

    if snapshot_views < latest_snapshot["views"]:
        st.sidebar.error(t("sidebar.snapshot.error.views_lower", language))
        has_invalid_snapshot = True

    if snapshot_likes < latest_snapshot["likes"]:
        st.sidebar.error(t("sidebar.snapshot.error.likes_lower", language))
        has_invalid_snapshot = True

    if snapshot_comments < latest_snapshot["comments"]:
        st.sidebar.error(t("sidebar.snapshot.error.comments_lower", language))
        has_invalid_snapshot = True

    if snapshot_saves < latest_snapshot["saves"]:
        st.sidebar.error(t("sidebar.snapshot.error.saves_lower", language))
        has_invalid_snapshot = True

    if snapshot_shares < latest_snapshot["shares"]:
        st.sidebar.error(t("sidebar.snapshot.error.shares_lower", language))
        has_invalid_snapshot = True

    return not has_invalid_snapshot


def _render_add_new_cover_form(
    language: str,
) -> None:
    """
    Render the sidebar form for adding a new cover and its initial metric snapshot.

    The form writes cover metadata to covers.csv and the first metric snapshot
    to metrics_snapshots.csv through src.data_manager.
    """
    st.sidebar.header(t("sidebar.add_cover.header", language))

    with st.sidebar.form(
        "add_cover_form",
        clear_on_submit=True,
    ):
        title = st.text_input(t("sidebar.add_cover.title", language))

        artist = st.text_input(t("sidebar.add_cover.artist", language))

        platform = st.selectbox(
            t("sidebar.add_cover.platform", language),
            ["Instagram", "YouTube", "TikTok"],
        )

        content_type = st.selectbox(
            t("sidebar.add_cover.content_type", language),
            ["Reels", "Shorts", "TikTok Video", "Post"],
        )

        genre = st.text_input(
            t("sidebar.add_cover.genre", language),
            placeholder=t(
                "sidebar.add_cover.genre_placeholder",
                language,
            ),
        )

        post_date = st.date_input(t("sidebar.add_cover.post_date", language))

        views = st.number_input(
            t("sidebar.add_cover.views", language),
            min_value=1,
            step=100,
        )

        likes = st.number_input(
            t("sidebar.add_cover.likes", language),
            min_value=0,
            step=10,
        )

        comments = st.number_input(
            t("sidebar.add_cover.comments", language),
            min_value=0,
            step=1,
        )

        saves = st.number_input(
            t("sidebar.add_cover.saves", language),
            min_value=0,
            step=1,
        )

        shares = st.number_input(
            t("sidebar.add_cover.shares", language),
            min_value=0,
            step=1,
        )

        duration_sec = st.number_input(
            t("sidebar.add_cover.duration_seconds", language),
            min_value=1,
            step=1,
        )

        hook_type = st.selectbox(
            t("sidebar.add_cover.hook_type", language),
            [
                "direct chorus",
                "slow intro",
                "instrumental intro",
                "vocal intro",
                "other",
            ],
        )

        vocal_style = st.selectbox(
            t("sidebar.add_cover.vocal_style", language),
            [
                "soft",
                "powerful",
                "emotional",
                "mixed",
                "other",
            ],
        )

        cover_language = st.selectbox(
            t("sidebar.add_cover.cover_language", language),
            ["Turkish", "English", "Other"],
        )

        post_time = st.time_input(t("sidebar.add_cover.post_time", language))

        caption_text = st.text_area(
            t("sidebar.add_cover.caption_text", language),
            placeholder="Paste or write the caption here",
        )

        hashtags = st.text_input(
            t("sidebar.add_cover.hashtags", language),
            placeholder="#cover #music #acoustic",
        )

        audio_quality_score = st.slider(
            t("sidebar.add_cover.audio_quality_score", language),
            min_value=1,
            max_value=5,
            value=3,
        )

        thumbnail_score = st.slider(
            t("sidebar.add_cover.thumbnail_score", language),
            min_value=1,
            max_value=5,
            value=3,
        )

        recording_type = st.selectbox(
            t("sidebar.add_cover.recording_type", language),
            ["home", "studio", "live", "other"],
        )

        arrangement_type = st.selectbox(
            t("sidebar.add_cover.arrangement_type", language),
            [
                "acoustic",
                "piano",
                "full band",
                "guitar vocal",
                "other",
            ],
        )

        song_mood = st.selectbox(
            t("sidebar.add_cover.song_mood", language),
            [
                "emotional",
                "energetic",
                "melancholic",
                "romantic",
                "dark",
                "other",
            ],
        )

        content_origin = st.selectbox(
            t("sidebar.add_cover.content_origin", language),
            ["cover", "original"],
        )

        submitted = st.form_submit_button(t("sidebar.add_cover.submit", language))

        if submitted:
            if title.strip() == "" or artist.strip() == "" or genre.strip() == "":
                st.warning(t("sidebar.add_cover.required_fields", language))
                return

            covers_df = load_covers_raw()
            snapshots_df = load_snapshots_raw()

            new_cover_id = _generate_next_id(
                covers_df,
                "cover_id",
                "C",
            )

            new_snapshot_id = _generate_next_id(
                snapshots_df,
                "snapshot_id",
                "S",
            )

            clean_hashtags = hashtags.strip()
            hashtag_count = _calculate_hashtag_count(clean_hashtags)

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
                "language": cover_language,
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
                "snapshot_date": (pd.Timestamp.today().date().isoformat()),
                "views": views,
                "likes": likes,
                "comments": comments,
                "saves": saves,
                "shares": shares,
            }

            append_new_cover(new_cover)
            append_metric_snapshot(new_snapshot)

            st.success(t("sidebar.add_cover.success", language))

            st.rerun()


def _render_add_metric_snapshot_form(
    language: str,
) -> None:
    """
    Render the sidebar form for adding a new metric snapshot to an existing cover.
    """
    st.sidebar.divider()
    st.sidebar.header(t("sidebar.snapshot.header", language))

    covers_for_snapshot = load_covers_raw()

    if covers_for_snapshot.empty:
        st.sidebar.info(t("sidebar.snapshot.no_covers", language))
        return

    covers_for_snapshot["display_name"] = (
        covers_for_snapshot["cover_id"]
        + " - "
        + covers_for_snapshot["title"]
        + " / "
        + covers_for_snapshot["artist"]
    )

    selected_cover_display = st.sidebar.selectbox(
        t("sidebar.snapshot.select_cover", language),
        covers_for_snapshot["display_name"].tolist(),
    )

    selected_cover_id = selected_cover_display.split(" - ")[0]

    snapshots_df = load_snapshots_raw()

    latest_snapshot = _get_latest_snapshot(
        snapshots_df,
        selected_cover_id,
    )

    _render_latest_snapshot_preview(
        latest_snapshot,
        language=language,
    )

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
        snapshot_date = st.date_input(t("sidebar.snapshot.snapshot_date", language))

        snapshot_views = st.number_input(
            t("sidebar.snapshot.snapshot_views", language),
            min_value=0,
            value=default_views,
            step=1,
        )

        snapshot_likes = st.number_input(
            t("sidebar.snapshot.snapshot_likes", language),
            min_value=0,
            value=default_likes,
            step=1,
        )

        snapshot_comments = st.number_input(
            t("sidebar.snapshot.snapshot_comments", language),
            min_value=0,
            value=default_comments,
            step=1,
        )

        snapshot_saves = st.number_input(
            t("sidebar.snapshot.snapshot_saves", language),
            min_value=0,
            value=default_saves,
            step=1,
        )

        snapshot_shares = st.number_input(
            t("sidebar.snapshot.snapshot_shares", language),
            min_value=0,
            value=default_shares,
            step=1,
        )

        snapshot_submitted = st.form_submit_button(
            t("sidebar.snapshot.submit", language)
        )

        if snapshot_submitted:
            snapshots_df = load_snapshots_raw()

            is_valid_snapshot = _validate_new_snapshot_values(
                latest_snapshot,
                snapshot_views,
                snapshot_likes,
                snapshot_comments,
                snapshot_saves,
                snapshot_shares,
                language=language,
            )

            if not is_valid_snapshot:
                st.stop()

            new_snapshot_id = _generate_next_id(
                snapshots_df,
                "snapshot_id",
                "S",
            )

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
                t(
                    "sidebar.snapshot.difference",
                    language,
                ).format(
                    views=views_diff,
                    likes=likes_diff,
                    comments=comments_diff,
                    saves=saves_diff,
                    shares=shares_diff,
                )
            )

            append_metric_snapshot(new_snapshot)

            st.success(t("sidebar.snapshot.success", language))

            st.rerun()


def render_sidebar_forms(
    language: str,
) -> None:
    """
    Render all sidebar forms used for cover and metric snapshot entry.
    """
    _render_add_new_cover_form(
        language=language,
    )

    _render_add_metric_snapshot_form(
        language=language,
    )
