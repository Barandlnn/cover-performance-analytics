import pandas as pd
import streamlit as st

from src.analyzer import (
    load_data,
    calculate_metrics,
    get_top_covers,
    generate_insights,
)

DATA_PATH = "data/covers.csv"


st.set_page_config(page_title="Cover Performance Analytics", layout="wide")

st.title("Cover Performance Analytics")
st.write("Analyze your cover performances across platforms.")


# -----------------------------
# LOAD RAW DATA
# -----------------------------

raw_df = load_data(DATA_PATH)


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

    submitted = st.form_submit_button("Add Cover")

    if submitted:
        if title.strip() == "" or artist.strip() == "" or genre.strip() == "":
            st.warning("Please fill title, artist and genre fields.")
        else:
            new_cover = {
                "title": title,
                "artist": artist,
                "platform": platform,
                "content_type": content_type,
                "genre": genre,
                "post_date": str(post_date),
                "views": views,
                "likes": likes,
                "comments": comments,
                "saves": saves,
                "shares": shares,
                "duration_sec": duration_sec,
                "hook_type": hook_type,
                "vocal_style": vocal_style,
                "language": language,
            }

            new_row = pd.DataFrame([new_cover])

            updated_df = pd.concat([raw_df, new_row], ignore_index=True)

            updated_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")

            st.success("Cover added successfully!")

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
            "title",
            "artist",
            "platform",
            "content_type",
            "genre",
            "post_date",
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
            "title",
            "artist",
            "platform",
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
