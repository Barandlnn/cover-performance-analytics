"""
Lightweight internationalization helpers for the Streamlit UI.

This module keeps user-facing UI text separate from the data model,
analytics logic, and Streamlit section code.
"""

DEFAULT_LANGUAGE = "en"

LANGUAGE_OPTIONS = {
    "English": "en",
    "Türkçe": "tr",
}

LANGUAGE_LABELS = {
    "en": "English",
    "tr": "Türkçe",
}


TRANSLATIONS = {
    "en": {
        "app.title": "Cover Performance Analytics",
        "app.caption": "Track cover performance, analyze patterns, and evaluate next cover candidates.",
        "language.selector_label": "Language",
        "language.english": "English",
        "language.turkish": "Turkish",
        "common.no_data": "No data available.",
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.success": "Saved successfully.",
        "common.warning": "Warning",
        "common.error": "Error",
        "section.main_dashboard": "Main Dashboard",
        "section.growth_analytics": "Growth Analytics",
        "section.pattern_analytics": "Pattern Analytics",
        "section.candidate_history": "Candidate Test History",
        "sidebar.add_cover.header": "Add New Cover",
        "sidebar.add_cover.title": "Cover Title",
        "sidebar.add_cover.artist": "Original Artist",
        "sidebar.add_cover.platform": "Platform",
        "sidebar.add_cover.content_type": "Content Type",
        "sidebar.add_cover.genre": "Genre",
        "sidebar.add_cover.genre_placeholder": "Example: Rock Acoustic",
        "sidebar.add_cover.post_date": "Post Date",
        "sidebar.add_cover.views": "Views",
        "sidebar.add_cover.likes": "Likes",
        "sidebar.add_cover.comments": "Comments",
        "sidebar.add_cover.saves": "Saves",
        "sidebar.add_cover.shares": "Shares",
        "sidebar.add_cover.duration_seconds": "Duration Seconds",
        "sidebar.add_cover.hook_type": "Hook Type",
        "sidebar.add_cover.vocal_style": "Vocal Style",
        "sidebar.add_cover.cover_language": "Cover Language",
        "sidebar.add_cover.post_time": "Post Time",
        "sidebar.add_cover.caption_text": "Caption Text",
        "sidebar.add_cover.hashtags": "Hashtags",
        "sidebar.add_cover.audio_quality_score": "Audio Quality Score",
        "sidebar.add_cover.thumbnail_score": "Thumbnail Score",
        "sidebar.add_cover.recording_type": "Recording Type",
        "sidebar.add_cover.arrangement_type": "Arrangement Type",
        "sidebar.add_cover.song_mood": "Song Mood",
        "sidebar.add_cover.content_origin": "Content Origin",
        "sidebar.add_cover.submit": "Add Cover",
        "sidebar.add_cover.required_fields": "Please fill title, artist and genre fields.",
        "sidebar.add_cover.success": "Cover and first metric snapshot added successfully!",
        "sidebar.snapshot.header": "Add Metric Snapshot",
        "sidebar.snapshot.no_covers": "No covers available for snapshot.",
        "sidebar.snapshot.select_cover": "Select Cover",
        "sidebar.snapshot.latest_preview": "Latest snapshot for selected cover:",
        "sidebar.snapshot.date": "Date",
        "sidebar.snapshot.views": "Views",
        "sidebar.snapshot.likes": "Likes",
        "sidebar.snapshot.comments": "Comments",
        "sidebar.snapshot.saves": "Saves",
        "sidebar.snapshot.shares": "Shares",
        "sidebar.snapshot.snapshot_date": "Snapshot Date",
        "sidebar.snapshot.snapshot_views": "Snapshot Views",
        "sidebar.snapshot.snapshot_likes": "Snapshot Likes",
        "sidebar.snapshot.snapshot_comments": "Snapshot Comments",
        "sidebar.snapshot.snapshot_saves": "Snapshot Saves",
        "sidebar.snapshot.snapshot_shares": "Snapshot Shares",
        "sidebar.snapshot.submit": "Add Snapshot",
        "sidebar.snapshot.success": "Metric snapshot added successfully!",
        "sidebar.snapshot.unknown_date": "Unknown",
        "sidebar.snapshot.error.views_lower": "New views value cannot be lower than the latest snapshot.",
        "sidebar.snapshot.error.likes_lower": "New likes value cannot be lower than the latest snapshot.",
        "sidebar.snapshot.error.comments_lower": "New comments value cannot be lower than the latest snapshot.",
        "sidebar.snapshot.error.saves_lower": "New saves value cannot be lower than the latest snapshot.",
        "sidebar.snapshot.error.shares_lower": "New shares value cannot be lower than the latest snapshot.",
        "sidebar.snapshot.difference": (
            "Snapshot difference → Views: {views}, Likes: {likes}, "
            "Comments: {comments}, Saves: {saves}, Shares: {shares}"
        ),
        "filters.header": "Filters",
        "filters.platform_label": "Platform Filter",
        "filters.genre_label": "Genre Filter",
        "filters.all_option": "All",
        "filters.empty_warning": "No covers found for the selected filters.",
        "main_dashboard.overview_title": "Overview",
        "main_dashboard.total_covers": "Total Covers",
        "main_dashboard.avg_engagement_rate": "Avg Engagement Rate",
        "main_dashboard.avg_save_rate": "Avg Save Rate",
        "main_dashboard.best_score": "Best Score",
        "main_dashboard.all_covers_title": "All Covers",
        "main_dashboard.no_cover_table_columns": (
            "No displayable columns found for the cover table."
        ),
        "main_dashboard.top_covers_title": "Top Performing Covers",
        "main_dashboard.no_top_cover_data": "No top cover data available yet.",
        "main_dashboard.no_top_table_columns": (
            "No displayable columns found for the top covers table."
        ),
        "main_dashboard.performance_chart_title": "Performance Score Chart",
        "main_dashboard.performance_chart_unavailable": (
            "Performance chart cannot be displayed."
        ),
        "main_dashboard.missing_columns": "Missing columns",
        "main_dashboard.no_performance_chart_data": (
            "No data available for the performance chart."
        ),
        "main_dashboard.quick_insights_title": "Quick Insights",
        "main_dashboard.no_insight_data": ("No cover data available for insights yet."),
        "main_dashboard.best_performing_cover": "Best performing cover",
        "main_dashboard.artist_label": "Artist",
        "main_dashboard.genre_label": "Genre",
        "main_dashboard.hook_type_label": "Hook type",
        "main_dashboard.vocal_style_label": "Vocal style",
        "main_dashboard.performance_score_label": "Performance score",
        "main_dashboard.engagement_rate_label": "Engagement rate",
        "main_dashboard.save_rate_label": "Save rate",
        "main_dashboard.share_rate_label": "Share rate",
        "main_dashboard.insight_summary": (
            "This result suggests that this type of cover may match "
            "your audience better. To make stronger conclusions, "
            "add more real cover data."
        ),
        "main_dashboard.ai_interpretation_title": "AI-Like Interpretation",
        "main_dashboard.insights_generation_failed": (
            "Insights could not be generated."
        ),
        "main_dashboard.missing_column": "Missing column",
        "analyzer.insights.above_average_save_rate": (
            "This cover has an above-average save rate. "
            "This may suggest that people wanted to revisit or remember "
            "this performance."
        ),
        "analyzer.insights.above_average_share_rate": (
            "This cover has an above-average share rate. "
            "This may indicate that the song or performance felt "
            "shareable to the audience."
        ),
        "analyzer.insights.above_average_comment_rate": (
            "This cover has an above-average comment rate. "
            "This may suggest that it triggered a stronger audience "
            "reaction or discussion."
        ),
        "analyzer.insights.best_score_below_average_views": (
            "This cover did not have the highest view count, but it "
            "produced the best performance score. This means the audience "
            "quality may be stronger than the raw reach."
        ),
        "analyzer.insights.direct_chorus_hook": (
            "The cover starts with a direct chorus hook. "
            "This can work well because the audience reaches the "
            "recognizable part quickly."
        ),
        "analyzer.insights.slow_intro_hook": (
            "The cover uses a slow intro. This may work well when the "
            "emotional buildup is strong, but it can also risk early "
            "drop-off."
        ),
        "analyzer.insights.strong_vocal_style": (
            "The vocal style is {vocal_style}. This may be one reason "
            "why the cover created stronger engagement."
        ),
        "analyzer.insights.strongest_genre": (
            "{genre} is currently the strongest genre in your dataset. "
            "You may want to test more covers in this direction."
        ),
        "analyzer.insights.small_dataset": (
            "Your dataset is still small. Add at least 10 real covers "
            "before making strong content decisions."
        ),
        "growth.title": "📈 Growth Analytics",
        "growth.caption": "Analyzes how cover performance develops over time.",
        "growth.insufficient_data": (
            "There is not enough snapshot data for growth analysis yet. "
            "At least 2 snapshots are required for a cover."
        ),
        "growth.missing_snapshots_file": (
            "The metrics_snapshots.csv file could not be found. "
            "Add at least one metric snapshot first."
        ),
        "growth.load_error": "An error occurred while loading Growth Analytics",
        "growth.summary.title": "🚀 Growth Summary",
        "growth.summary.best_views": "Best Views Growth",
        "growth.summary.best_likes": "Best Likes Growth",
        "growth.summary.best_engagement": "Best Engagement Growth",
        "growth.summary.debug_columns": "Debug: Growth Summary Columns",
        "growth.history.title": "📊 Selected Cover Snapshot History",
        "growth.history.no_covers": (
            "Add at least one cover before displaying snapshot history."
        ),
        "growth.history.selector": "Select a cover to inspect snapshot history",
        "growth.history.no_history": (
            "No snapshot history has been found for this cover yet."
        ),
        "growth.history.views_trend": "📈 Views Trend",
        "growth.history.engagement_trend": "❤️ Engagement Trend",
        "pattern.title": "📊 V2 Pattern Analytics",
        "pattern.caption": (
            "Analyzes which genres, artists, and content types perform "
            "better based on the latest metrics and growth data."
        ),
        "pattern.unavailable": (
            "Pattern analytics is not available yet. "
            "Required columns may be missing."
        ),
        "pattern.load_error": ("Pattern analytics could not be loaded"),
        "pattern.insights.title": "🧠 V2 Pattern Insights",
        "pattern.recommendations.title": ("🎯 V2 Cover Planning Recommendations"),
        "pattern.recommendations.empty": (
            "No planning recommendations are available yet."
        ),
        "pattern.recommendations.top": (
            "Top recommendation: {pattern} ({dimension}) — " "{priority}. {action}"
        ),
        "pattern.candidate.title": ("🧪 V2 Next Cover Candidate Test"),
        "pattern.candidate.caption": (
            "Select a possible future cover profile and estimate how "
            "strong it looks based on the current pattern data."
        ),
        "pattern.candidate.not_available": "Not available",
        "pattern.candidate.genre": "Candidate Genre",
        "pattern.candidate.artist": "Candidate Artist",
        "pattern.candidate.content_type": ("Candidate Content Type"),
        "pattern.candidate.analyze": "Analyze Candidate Cover",
        "pattern.candidate.score": "Candidate Score",
        "pattern.candidate.explanation_title": ("🧠 Candidate Explanation"),
        "pattern.candidate.save": "Save Candidate Test Result",
        "pattern.candidate.save_success": ("Candidate test result saved successfully."),
        "pattern.candidate.label.strong": "Strong Candidate",
        "pattern.candidate.label.promising": ("Promising Candidate"),
        "pattern.candidate.label.needs_more_data": ("Interesting but Needs More Data"),
        "pattern.candidate.label.experimental": ("Experimental Candidate"),
        "pattern.candidate.label.weak": "Weak Candidate",
        "pattern.candidate.action.strong": (
            "This is a strong cover idea. " "It is reasonable to prioritize it."
        ),
        "pattern.candidate.action.promising": (
            "This cover idea is worth testing soon."
        ),
        "pattern.candidate.action.needs_more_data": (
            "This idea looks interesting, but you should test it "
            "carefully and collect more data."
        ),
        "pattern.candidate.action.experimental": (
            "This can be tested as an experiment, but do not "
            "prioritize it over stronger patterns."
        ),
        "pattern.candidate.action.weak": (
            "This idea is weak based on the current dataset."
        ),
        "pattern.dynamic.dimension.genre": "genre",
        "pattern.dynamic.dimension.artist": "artist",
        "pattern.dynamic.dimension.content_type": ("content type"),
        "pattern.dynamic.confidence.high": "high",
        "pattern.dynamic.confidence.medium": "medium",
        "pattern.dynamic.confidence.low": "low",
        "pattern.dynamic.confidence.unknown": "unknown",
        "pattern.dynamic.decision.strong": "Strong Pattern",
        "pattern.dynamic.decision.promising": ("Promising Pattern"),
        "pattern.dynamic.decision.needs_more_data": ("Needs More Data"),
        "pattern.dynamic.decision.weak": "Weak Pattern",
        "pattern.dynamic.decision.unknown": "Unknown",
        "pattern.dynamic.priority.high": "High Priority",
        "pattern.dynamic.priority.medium": "Medium Priority",
        "pattern.dynamic.priority.data_needed": "Data Needed",
        "pattern.dynamic.priority.low": "Low Priority",
        "pattern.dynamic.recommendation.strong": (
            "Prioritize this pattern in future cover planning."
        ),
        "pattern.dynamic.recommendation.promising": (
            "Test this pattern with a few more covers."
        ),
        "pattern.dynamic.recommendation.needs_more_data": (
            "Do not make a strong decision yet; " "collect more data first."
        ),
        "pattern.dynamic.recommendation.weak": (
            "This pattern is not strong enough to prioritize " "right now."
        ),
        "pattern.dynamic.insight.best": (
            "Best weighted {dimension}: {name}. "
            "Weighted pattern score is {weighted_score}, while "
            "the raw average score is {avg_score}. "
            "This result is based on {cover_count} cover(s), "
            "confidence is {confidence}, and the decision label "
            "is '{decision_label}'. {recommendation}"
        ),
        "pattern.dynamic.insight.gap": (
            "{best_name} is ahead of {second_name} by "
            "{weighted_gap} weighted score points in the "
            "{dimension} analysis."
        ),
        "pattern.dynamic.insight.needs_more_data": (
            "Some {dimension} patterns look interesting but "
            "still need more data: {names}."
        ),
        "pattern.dynamic.insight.not_enough": (
            "Not enough pattern data is available yet."
        ),
        "pattern.dynamic.planning_action.strong": (
            "Plan more covers using this {dimension}."
        ),
        "pattern.dynamic.planning_action.promising": (
            "Test this {dimension} with 2-3 more covers."
        ),
        "pattern.dynamic.planning_action.needs_more_data": (
            "Collect more data before making a strong decision "
            "about this {dimension}."
        ),
        "pattern.dynamic.planning_action.weak": (
            "Do not prioritize this {dimension} right now."
        ),
        "pattern.dynamic.recommendation.reason": (
            "{pattern} has a raw average score of {avg_score}, "
            "a weighted score of {weighted_score}, "
            "{cover_count} cover(s), and {confidence} confidence."
        ),
        "pattern.dynamic.candidate.empty": ("No candidate details are available."),
        "pattern.dynamic.candidate.classification": (
            "This candidate is classified as "
            "'{candidate_label}' with a score of "
            "{candidate_score}."
        ),
        "pattern.dynamic.candidate.strong_support": (
            "The strongest support for this candidate comes " "from: {patterns}."
        ),
        "pattern.dynamic.candidate.promising_support": (
            "These parts look promising but still need more " "validation: {patterns}."
        ),
        "pattern.dynamic.candidate.needs_data": (
            "These parts need more data before making a strong " "decision: {patterns}."
        ),
        "pattern.dynamic.candidate.not_found": (
            "These selected patterns were not found in the "
            "current dataset: {patterns}."
        ),
        "pattern.dynamic.candidate.multiple_low_confidence": (
            "This idea should be tested carefully because "
            "multiple parts of the candidate have low data "
            "confidence."
        ),
        "pattern.dynamic.candidate.final.strong": (
            "This cover idea can be prioritized in the " "near-term cover plan."
        ),
        "pattern.dynamic.candidate.final.promising": (
            "This cover idea can be added to the near-term " "testing list."
        ),
        "pattern.dynamic.candidate.final.needs_more_data": (
            "This idea is not a guaranteed priority yet, but it "
            "is worth testing carefully because at least one "
            "part of the candidate has strong support."
        ),
        "pattern.dynamic.candidate.final.experimental": (
            "This cover idea is better suited for experimentation "
            "rather than priority planning."
        ),
        "pattern.dynamic.candidate.final.weak": (
            "This cover idea should not be prioritized until " "stronger data appears."
        ),
        "candidate_history.insights.no_history": (
            "No candidate test history is available yet."
        ),
        "candidate_history.insights.total_tests": (
            "{total_tests} candidate cover ideas have been tested so far."
        ),
        "candidate_history.insights.average_score": (
            "The average candidate score is {average_score}."
        ),
        "candidate_history.insights.best_candidate": (
            "Best candidate so far: {genre} / {artist} / "
            "{content_type} — score: {candidate_score}."
        ),
        "candidate_history.insights.best_genre": (
            "The best tested genre is {genre}, with an average "
            "score of {average_score}."
        ),
        "candidate_history.insights.strong_count": (
            "Strong Candidate classifications: {count}."
        ),
        "candidate_history.insights.needs_more_data_count": (
            "Tests requiring more data before a strong decision: {count}."
        ),
        "candidate_history.title": "Candidate Test History",
        "candidate_history.file_not_found": (
            "No candidate test history file was found yet."
        ),
        "candidate_history.load_error": (
            "An error occurred while loading candidate history: {error}"
        ),
        "candidate_history.empty": ("No candidate tests have been saved yet."),
        "candidate_history.summary_title": ("Candidate History Summary"),
        "candidate_history.insights_title": ("Candidate History Insights"),
        "candidate_history.top_candidates_title": ("Top Candidate Tests"),
        "candidate_history.genre_performance_title": (
            "Genre-Based Candidate Performance"
        ),
        "candidate_history.genre_data_insufficient": (
            "There is not enough data for genre-based analysis."
        ),
        "candidate_history.columns.test_date": "Test Date",
        "candidate_history.columns.genre": "Genre",
        "candidate_history.columns.artist": "Artist",
        "candidate_history.columns.content_type": "Content Type",
        "candidate_history.columns.candidate_score": "Candidate Score",
        "candidate_history.columns.candidate_label": "Candidate Label",
        "candidate_history.columns.needs_more_data_count": ("Needs More Data Count"),
        "candidate_history.columns.action": "Action",
        "candidate_history.columns.total_tests": "Total Tests",
        "candidate_history.columns.average_candidate_score": (
            "Average Candidate Score"
        ),
        "candidate_history.columns.best_candidate_score": ("Best Candidate Score"),
        "candidate_history.columns.strong_candidate_count": ("Strong Candidate Count"),
        "candidate_history.columns.promising_candidate_count": (
            "Promising Candidate Count"
        ),
        "candidate_history.columns.test_count": "Test Count",
        "candidate_history.columns.average_score": "Average Score",
        "candidate_history.columns.best_score": "Best Score",
        "candidate_history.values.candidate_label."
        "interesting_but_needs_more_data": ("Interesting but Needs More Data"),
        "candidate_history.values.action."
        "test_carefully_collect_more_data": (
            "This idea looks interesting, but you should test it "
            "carefully and collect more data."
        ),
    },
    "tr": {
        "app.title": "Cover Performans Analitiği",
        "app.caption": "Cover performansını takip et, kalıpları analiz et ve sonraki cover adaylarını değerlendir.",
        "language.selector_label": "Dil",
        "language.english": "İngilizce",
        "language.turkish": "Türkçe",
        "common.no_data": "Veri bulunamadı.",
        "common.save": "Kaydet",
        "common.cancel": "İptal",
        "common.success": "Başarıyla kaydedildi.",
        "common.warning": "Uyarı",
        "common.error": "Hata",
        "section.main_dashboard": "Ana Dashboard",
        "section.growth_analytics": "Büyüme Analitiği",
        "section.pattern_analytics": "Kalıp Analitiği",
        "section.candidate_history": "Aday Test Geçmişi",
        "sidebar.add_cover.header": "Yeni Cover Ekle",
        "sidebar.add_cover.title": "Cover Başlığı",
        "sidebar.add_cover.artist": "Orijinal Sanatçı",
        "sidebar.add_cover.platform": "Platform",
        "sidebar.add_cover.content_type": "İçerik Türü",
        "sidebar.add_cover.genre": "Müzik Türü",
        "sidebar.add_cover.genre_placeholder": "Örnek: Akustik Rock",
        "sidebar.add_cover.post_date": "Paylaşım Tarihi",
        "sidebar.add_cover.views": "Görüntülenme",
        "sidebar.add_cover.likes": "Beğeni",
        "sidebar.add_cover.comments": "Yorum",
        "sidebar.add_cover.saves": "Kaydetme",
        "sidebar.add_cover.shares": "Paylaşım",
        "sidebar.add_cover.duration_seconds": "Süre (Saniye)",
        "sidebar.add_cover.hook_type": "Hook Türü",
        "sidebar.add_cover.vocal_style": "Vokal Tarzı",
        "sidebar.add_cover.cover_language": "Cover Dili",
        "sidebar.add_cover.post_time": "Paylaşım Saati",
        "sidebar.add_cover.caption_text": "Açıklama Metni",
        "sidebar.add_cover.hashtags": "Hashtagler",
        "sidebar.add_cover.audio_quality_score": "Ses Kalitesi Puanı",
        "sidebar.add_cover.thumbnail_score": "Kapak Görseli Puanı",
        "sidebar.add_cover.recording_type": "Kayıt Türü",
        "sidebar.add_cover.arrangement_type": "Aranje Türü",
        "sidebar.add_cover.song_mood": "Şarkı Duygusu",
        "sidebar.add_cover.content_origin": "İçerik Kaynağı",
        "sidebar.add_cover.submit": "Cover Ekle",
        "sidebar.add_cover.required_fields": "Lütfen başlık, sanatçı ve müzik türü alanlarını doldurun.",
        "sidebar.add_cover.success": "Cover ve ilk metrik kaydı başarıyla eklendi!",
        "sidebar.snapshot.header": "Metrik Kaydı Ekle",
        "sidebar.snapshot.no_covers": "Metrik kaydı eklemek için cover bulunamadı.",
        "sidebar.snapshot.select_cover": "Cover Seç",
        "sidebar.snapshot.latest_preview": "Seçilen cover için son metrik kaydı:",
        "sidebar.snapshot.date": "Tarih",
        "sidebar.snapshot.views": "Görüntülenme",
        "sidebar.snapshot.likes": "Beğeni",
        "sidebar.snapshot.comments": "Yorum",
        "sidebar.snapshot.saves": "Kaydetme",
        "sidebar.snapshot.shares": "Paylaşım",
        "sidebar.snapshot.snapshot_date": "Metrik Tarihi",
        "sidebar.snapshot.snapshot_views": "Görüntülenme Değeri",
        "sidebar.snapshot.snapshot_likes": "Beğeni Değeri",
        "sidebar.snapshot.snapshot_comments": "Yorum Değeri",
        "sidebar.snapshot.snapshot_saves": "Kaydetme Değeri",
        "sidebar.snapshot.snapshot_shares": "Paylaşım Değeri",
        "sidebar.snapshot.submit": "Metrik Kaydı Ekle",
        "sidebar.snapshot.success": "Metrik kaydı başarıyla eklendi!",
        "sidebar.snapshot.unknown_date": "Bilinmiyor",
        "sidebar.snapshot.error.views_lower": "Yeni görüntülenme değeri son metrik kaydından düşük olamaz.",
        "sidebar.snapshot.error.likes_lower": "Yeni beğeni değeri son metrik kaydından düşük olamaz.",
        "sidebar.snapshot.error.comments_lower": "Yeni yorum değeri son metrik kaydından düşük olamaz.",
        "sidebar.snapshot.error.saves_lower": "Yeni kaydetme değeri son metrik kaydından düşük olamaz.",
        "sidebar.snapshot.error.shares_lower": "Yeni paylaşım değeri son metrik kaydından düşük olamaz.",
        "sidebar.snapshot.difference": (
            "Metrik farkı → Görüntülenme: {views}, Beğeni: {likes}, "
            "Yorum: {comments}, Kaydetme: {saves}, Paylaşım: {shares}"
        ),
        "filters.header": "Filtreler",
        "filters.platform_label": "Platform Filtresi",
        "filters.genre_label": "Tür Filtresi",
        "filters.all_option": "Tümü",
        "filters.empty_warning": "Seçilen filtrelere uygun cover bulunamadı.",
        "main_dashboard.overview_title": "Genel Bakış",
        "main_dashboard.total_covers": "Toplam Cover",
        "main_dashboard.avg_engagement_rate": "Ort. Etkileşim Oranı",
        "main_dashboard.avg_save_rate": "Ort. Kaydetme Oranı",
        "main_dashboard.best_score": "En İyi Skor",
        "main_dashboard.all_covers_title": "Tüm Coverlar",
        "main_dashboard.no_cover_table_columns": (
            "Cover tablosu için görüntülenebilir sütun bulunamadı."
        ),
        "main_dashboard.top_covers_title": "En İyi Performans Gösteren Coverlar",
        "main_dashboard.no_top_cover_data": (
            "Henüz en iyi performans gösteren cover verisi bulunmuyor."
        ),
        "main_dashboard.no_top_table_columns": (
            "En iyi coverlar tablosu için görüntülenebilir sütun bulunamadı."
        ),
        "main_dashboard.performance_chart_title": "Performans Skoru Grafiği",
        "main_dashboard.performance_chart_unavailable": (
            "Performans grafiği görüntülenemiyor."
        ),
        "main_dashboard.missing_columns": "Eksik sütunlar",
        "main_dashboard.no_performance_chart_data": (
            "Performans grafiği için kullanılabilir veri bulunmuyor."
        ),
        "main_dashboard.quick_insights_title": "Hızlı İçgörüler",
        "main_dashboard.no_insight_data": (
            "Henüz içgörü oluşturmak için cover verisi bulunmuyor."
        ),
        "main_dashboard.best_performing_cover": ("En iyi performans gösteren cover"),
        "main_dashboard.artist_label": "Sanatçı",
        "main_dashboard.genre_label": "Tür",
        "main_dashboard.hook_type_label": "Hook türü",
        "main_dashboard.vocal_style_label": "Vokal stili",
        "main_dashboard.performance_score_label": "Performans skoru",
        "main_dashboard.engagement_rate_label": "Etkileşim oranı",
        "main_dashboard.save_rate_label": "Kaydetme oranı",
        "main_dashboard.share_rate_label": "Paylaşım oranı",
        "main_dashboard.insight_summary": (
            "Bu sonuç, bu tür coverların kitlenizle daha iyi "
            "eşleşebileceğini gösteriyor. Daha güçlü sonuçlara ulaşmak "
            "için daha fazla gerçek cover verisi ekleyin."
        ),
        "main_dashboard.ai_interpretation_title": "Yapay Zekâ Benzeri Yorum",
        "main_dashboard.insights_generation_failed": ("İçgörüler oluşturulamadı."),
        "main_dashboard.missing_column": "Eksik sütun",
        "analyzer.insights.above_average_save_rate": (
            "Bu cover'ın kaydetme oranı ortalamanın üzerinde. "
            "Bu durum, insanların bu performansa yeniden dönmek veya "
            "onu hatırlamak istediğini gösterebilir."
        ),
        "analyzer.insights.above_average_share_rate": (
            "Bu cover'ın paylaşım oranı ortalamanın üzerinde. "
            "Bu durum, şarkının veya performansın kitle tarafından "
            "paylaşılmaya değer bulunduğunu gösterebilir."
        ),
        "analyzer.insights.above_average_comment_rate": (
            "Bu cover'ın yorum oranı ortalamanın üzerinde. "
            "Bu durum, performansın daha güçlü bir izleyici tepkisi "
            "veya tartışma oluşturduğunu gösterebilir."
        ),
        "analyzer.insights.best_score_below_average_views": (
            "Bu cover en yüksek görüntülenme sayısına ulaşmadı, ancak en "
            "iyi performans skorunu üretti. Bu, izleyici kalitesinin ham "
            "erişimden daha güçlü olabileceğini gösterir."
        ),
        "analyzer.insights.direct_chorus_hook": (
            "Cover doğrudan nakarat hook'u ile başlıyor. "
            "Kitlenin şarkının tanınan bölümüne hızlıca ulaşması bu "
            "yaklaşımın iyi çalışmasını sağlayabilir."
        ),
        "analyzer.insights.slow_intro_hook": (
            "Cover yavaş bir giriş kullanıyor. Bu yaklaşım duygusal "
            "yükseliş güçlü olduğunda iyi çalışabilir, ancak erken izleyici "
            "kaybı riski de oluşturabilir."
        ),
        "analyzer.insights.strong_vocal_style": (
            "Vokal stili {vocal_style}. Bu özellik, cover'ın daha güçlü "
            "etkileşim oluşturmasının nedenlerinden biri olabilir."
        ),
        "analyzer.insights.strongest_genre": (
            "{genre}, veri kümenizde şu anda en güçlü türdür. "
            "Bu yönde daha fazla cover test edebilirsiniz."
        ),
        "analyzer.insights.small_dataset": (
            "Veri kümeniz hâlâ küçük. Güçlü içerik kararları vermeden önce "
            "en az 10 gerçek cover verisi ekleyin."
        ),
        "growth.title": "📈 Büyüme Analitiği",
        "growth.caption": (
            "Cover performansının zaman içindeki gelişimini analiz eder."
        ),
        "growth.insufficient_data": (
            "Büyüme analizi için henüz yeterli snapshot verisi yok. "
            "Bir cover için en az 2 snapshot gereklidir."
        ),
        "growth.missing_snapshots_file": (
            "metrics_snapshots.csv dosyası bulunamadı. "
            "Önce en az bir metrik snapshot'ı eklemelisin."
        ),
        "growth.load_error": "Büyüme Analitiği yüklenirken bir hata oluştu",
        "growth.summary.title": "🚀 Büyüme Özeti",
        "growth.summary.best_views": "En İyi Görüntülenme Artışı",
        "growth.summary.best_likes": "En İyi Beğeni Artışı",
        "growth.summary.best_engagement": "En İyi Etkileşim Artışı",
        "growth.summary.debug_columns": "Hata Ayıklama: Büyüme Özeti Kolonları",
        "growth.history.title": "📊 Seçili Cover Snapshot Geçmişi",
        "growth.history.no_covers": (
            "Snapshot geçmişini göstermek için önce en az bir cover eklemelisin."
        ),
        "growth.history.selector": ("Snapshot geçmişini incelemek için bir cover seç"),
        "growth.history.no_history": (
            "Bu cover için henüz snapshot geçmişi bulunamadı."
        ),
        "growth.history.views_trend": "📈 Görüntülenme Trendi",
        "growth.history.engagement_trend": "❤️ Etkileşim Trendi",
        "pattern.title": "📊 V2 Örüntü Analitiği",
        "pattern.caption": (
            "En güncel metriklere ve büyüme verilerine göre hangi "
            "türlerin, sanatçıların ve içerik tiplerinin daha iyi "
            "performans gösterdiğini analiz eder."
        ),
        "pattern.unavailable": (
            "Örüntü analitiği henüz kullanılamıyor. "
            "Gerekli kolonlardan bazıları eksik olabilir."
        ),
        "pattern.load_error": ("Örüntü analitiği yüklenemedi"),
        "pattern.insights.title": "🧠 V2 Örüntü İçgörüleri",
        "pattern.recommendations.title": ("🎯 V2 Cover Planlama Önerileri"),
        "pattern.recommendations.empty": (
            "Henüz kullanılabilir bir planlama önerisi yok."
        ),
        "pattern.recommendations.top": (
            "En iyi öneri: {pattern} ({dimension}) — " "{priority}. {action}"
        ),
        "pattern.candidate.title": ("🧪 V2 Sonraki Cover Adayı Testi"),
        "pattern.candidate.caption": (
            "Gelecekte değerlendirebileceğin bir cover profilini seç "
            "ve mevcut örüntü verilerine göre ne kadar güçlü "
            "göründüğünü tahmin et."
        ),
        "pattern.candidate.not_available": "Kullanılamıyor",
        "pattern.candidate.genre": "Aday Tür",
        "pattern.candidate.artist": "Aday Sanatçı",
        "pattern.candidate.content_type": ("Aday İçerik Tipi"),
        "pattern.candidate.analyze": "Cover Adayını Analiz Et",
        "pattern.candidate.score": "Aday Puanı",
        "pattern.candidate.explanation_title": ("🧠 Aday Açıklaması"),
        "pattern.candidate.save": ("Aday Testi Sonucunu Kaydet"),
        "pattern.candidate.save_success": ("Aday testi sonucu başarıyla kaydedildi."),
        "pattern.candidate.label.strong": "Güçlü Aday",
        "pattern.candidate.label.promising": ("Umut Vadeden Aday"),
        "pattern.candidate.label.needs_more_data": (
            "İlgi Çekici ancak Daha Fazla Veri Gerekli"
        ),
        "pattern.candidate.label.experimental": ("Deneysel Aday"),
        "pattern.candidate.label.weak": "Zayıf Aday",
        "pattern.candidate.action.strong": (
            "Bu güçlü bir cover fikri. " "Önceliklendirilmesi mantıklı görünüyor."
        ),
        "pattern.candidate.action.promising": (
            "Bu cover fikri yakın zamanda test edilmeye değer."
        ),
        "pattern.candidate.action.needs_more_data": (
            "Bu fikir ilgi çekici görünüyor ancak dikkatli şekilde "
            "test edilmeli ve daha fazla veri toplanmalıdır."
        ),
        "pattern.candidate.action.experimental": (
            "Bu fikir deneysel olarak test edilebilir ancak daha güçlü "
            "örüntülerin önüne alınmamalıdır."
        ),
        "pattern.candidate.action.weak": (
            "Bu fikir mevcut veri setine göre zayıf görünüyor."
        ),
        "pattern.dynamic.dimension.genre": "tür",
        "pattern.dynamic.dimension.artist": "sanatçı",
        "pattern.dynamic.dimension.content_type": ("içerik tipi"),
        "pattern.dynamic.confidence.high": "yüksek",
        "pattern.dynamic.confidence.medium": "orta",
        "pattern.dynamic.confidence.low": "düşük",
        "pattern.dynamic.confidence.unknown": "bilinmiyor",
        "pattern.dynamic.decision.strong": "Güçlü Örüntü",
        "pattern.dynamic.decision.promising": ("Umut Vadeden Örüntü"),
        "pattern.dynamic.decision.needs_more_data": ("Daha Fazla Veri Gerekli"),
        "pattern.dynamic.decision.weak": "Zayıf Örüntü",
        "pattern.dynamic.decision.unknown": "Bilinmiyor",
        "pattern.dynamic.priority.high": "Yüksek Öncelik",
        "pattern.dynamic.priority.medium": "Orta Öncelik",
        "pattern.dynamic.priority.data_needed": ("Veri Gerekli"),
        "pattern.dynamic.priority.low": "Düşük Öncelik",
        "pattern.dynamic.recommendation.strong": (
            "Gelecekteki cover planlamasında bu örüntüye " "öncelik ver."
        ),
        "pattern.dynamic.recommendation.promising": (
            "Bu örüntüyü birkaç cover ile daha test et."
        ),
        "pattern.dynamic.recommendation.needs_more_data": (
            "Henüz güçlü bir karar verme; önce daha fazla " "veri topla."
        ),
        "pattern.dynamic.recommendation.weak": (
            "Bu örüntü şu anda önceliklendirilecek kadar " "güçlü değil."
        ),
        "pattern.dynamic.insight.best": (
            "Ağırlıklı {dimension} analizinde en iyi sonuç: "
            "{name}. Ağırlıklı örüntü puanı {weighted_score}, "
            "ham ortalama puan ise {avg_score}. "
            "Bu sonuç {cover_count} cover verisine dayanıyor; "
            "güven seviyesi {confidence} ve karar etiketi "
            "'{decision_label}'. {recommendation}"
        ),
        "pattern.dynamic.insight.gap": (
            "{best_name}, {dimension} analizinde "
            "{second_name} sonucunun {weighted_gap} ağırlıklı "
            "puan önünde bulunuyor."
        ),
        "pattern.dynamic.insight.needs_more_data": (
            "Bazı {dimension} örüntüleri ilgi çekici görünüyor "
            "ancak hâlâ daha fazla veriye ihtiyaç duyuyor: "
            "{names}."
        ),
        "pattern.dynamic.insight.not_enough": (
            "Henüz yeterli örüntü verisi bulunmuyor."
        ),
        "pattern.dynamic.planning_action.strong": (
            "Bu {dimension} için daha fazla cover planla."
        ),
        "pattern.dynamic.planning_action.promising": (
            "Bu {dimension} seçeneğini 2-3 cover ile daha " "test et."
        ),
        "pattern.dynamic.planning_action.needs_more_data": (
            "Bu {dimension} hakkında güçlü bir karar vermeden "
            "önce daha fazla veri topla."
        ),
        "pattern.dynamic.planning_action.weak": (
            "Bu {dimension} seçeneğini şu anda " "önceliklendirme."
        ),
        "pattern.dynamic.recommendation.reason": (
            "{pattern}; {avg_score} ham ortalama puana, "
            "{weighted_score} ağırlıklı puana, "
            "{cover_count} cover verisine ve {confidence} "
            "güven seviyesine sahip."
        ),
        "pattern.dynamic.candidate.empty": (
            "Adayla ilgili kullanılabilir ayrıntı bulunmuyor."
        ),
        "pattern.dynamic.candidate.classification": (
            "Bu aday, {candidate_score} puanla "
            "'{candidate_label}' olarak sınıflandırıldı."
        ),
        "pattern.dynamic.candidate.strong_support": (
            "Bu adaya en güçlü desteği sağlayan seçimler: " "{patterns}."
        ),
        "pattern.dynamic.candidate.promising_support": (
            "Bu seçimler umut vadetmektedir ancak daha fazla "
            "doğrulamaya ihtiyaç duyar: {patterns}."
        ),
        "pattern.dynamic.candidate.needs_data": (
            "Bu seçimler hakkında güçlü bir karar vermeden önce "
            "daha fazla veri gereklidir: {patterns}."
        ),
        "pattern.dynamic.candidate.not_found": (
            "Seçilen bu örüntüler mevcut veri setinde " "bulunamadı: {patterns}."
        ),
        "pattern.dynamic.candidate.multiple_low_confidence": (
            "Adayın birden fazla bileşeni düşük veri güvenine "
            "sahip olduğu için bu fikir dikkatli şekilde "
            "test edilmelidir."
        ),
        "pattern.dynamic.candidate.final.strong": (
            "Bu cover fikri yakın dönem cover planında " "önceliklendirilebilir."
        ),
        "pattern.dynamic.candidate.final.promising": (
            "Bu cover fikri yakın dönem test listesine " "eklenebilir."
        ),
        "pattern.dynamic.candidate.final.needs_more_data": (
            "Bu fikir henüz kesin bir öncelik değildir ancak "
            "adayın en az bir bileşeni güçlü destek aldığı için "
            "dikkatli şekilde test edilmeye değerdir."
        ),
        "pattern.dynamic.candidate.final.experimental": (
            "Bu cover fikri öncelikli planlamadan çok deneysel "
            "bir test için uygundur."
        ),
        "pattern.dynamic.candidate.final.weak": (
            "Daha güçlü veriler ortaya çıkana kadar bu cover "
            "fikri önceliklendirilmemelidir."
        ),
        "candidate_history.insights.no_history": (
            "Henüz candidate test geçmişi bulunmuyor."
        ),
        "candidate_history.insights.total_tests": (
            "Şu ana kadar {total_tests} cover adayı test edildi."
        ),
        "candidate_history.insights.average_score": (
            "Ortalama candidate skoru {average_score}."
        ),
        "candidate_history.insights.best_candidate": (
            "Şu ana kadarki en iyi aday: {genre} / {artist} / "
            "{content_type} — skor: {candidate_score}."
        ),
        "candidate_history.insights.best_genre": (
            "Test edilen en başarılı tür {genre}; ortalama " "skoru {average_score}."
        ),
        "candidate_history.insights.strong_count": (
            "Güçlü Aday olarak sınıflandırılan test sayısı: {count}."
        ),
        "candidate_history.insights.needs_more_data_count": (
            "Güçlü bir karar öncesinde daha fazla veri gerektiren "
            "test sayısı: {count}."
        ),
        "candidate_history.title": "Aday Test Geçmişi",
        "candidate_history.file_not_found": (
            "Henüz aday test geçmişi dosyası bulunamadı."
        ),
        "candidate_history.load_error": (
            "Aday geçmişi yüklenirken bir hata oluştu: {error}"
        ),
        "candidate_history.empty": ("Henüz kaydedilmiş bir aday testi bulunmuyor."),
        "candidate_history.summary_title": ("Aday Geçmişi Özeti"),
        "candidate_history.insights_title": ("Aday Geçmişi Yorumları"),
        "candidate_history.top_candidates_title": ("En İyi Aday Testleri"),
        "candidate_history.genre_performance_title": ("Türe Göre Aday Performansı"),
        "candidate_history.genre_data_insufficient": (
            "Türe göre analiz için yeterli veri bulunmuyor."
        ),
        "candidate_history.columns.test_date": "Test Tarihi",
        "candidate_history.columns.genre": "Tür",
        "candidate_history.columns.artist": "Sanatçı",
        "candidate_history.columns.content_type": "İçerik Türü",
        "candidate_history.columns.candidate_score": "Aday Skoru",
        "candidate_history.columns.candidate_label": "Aday Sınıfı",
        "candidate_history.columns.needs_more_data_count": (
            "Daha Fazla Veri Gereksinimi"
        ),
        "candidate_history.columns.action": "Önerilen Aksiyon",
        "candidate_history.columns.total_tests": "Toplam Test",
        "candidate_history.columns.average_candidate_score": ("Ortalama Aday Skoru"),
        "candidate_history.columns.best_candidate_score": ("En İyi Aday Skoru"),
        "candidate_history.columns.strong_candidate_count": ("Güçlü Aday Sayısı"),
        "candidate_history.columns.promising_candidate_count": (
            "Umut Vadeden Aday Sayısı"
        ),
        "candidate_history.columns.test_count": "Test Sayısı",
        "candidate_history.columns.average_score": "Ortalama Skor",
        "candidate_history.columns.best_score": "En İyi Skor",
    },
    "candidate_history.values.candidate_label."
    "interesting_but_needs_more_data": ("İlgi Çekici, Ancak Daha Fazla Veri Gerekiyor"),
    "candidate_history.values.action."
    "test_carefully_collect_more_data": (
        "Bu fikir ilgi çekici görünüyor; ancak dikkatli şekilde "
        "test etmeli ve daha fazla veri toplamalısın."
    ),
}


def get_language_code(language_label: str) -> str:
    """
    Convert a user-facing language label into an internal language code.

    Example:
        "English" -> "en"
        "Türkçe" -> "tr"
    """
    return LANGUAGE_OPTIONS.get(language_label, DEFAULT_LANGUAGE)


def get_language_label(language_code: str) -> str:
    """
    Convert an internal language code into a user-facing language label.

    Example:
        "en" -> "English"
        "tr" -> "Türkçe"
    """
    return LANGUAGE_LABELS.get(language_code, LANGUAGE_LABELS[DEFAULT_LANGUAGE])


def t(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Return the translated text for the given key and language.

    Fallback order:
    1. Requested language translation
    2. English translation
    3. Translation key itself
    """
    language_translations = TRANSLATIONS.get(language, {})
    english_translations = TRANSLATIONS.get(DEFAULT_LANGUAGE, {})

    return language_translations.get(
        key,
        english_translations.get(key, key),
    )
