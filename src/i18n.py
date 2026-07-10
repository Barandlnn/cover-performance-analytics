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
    },
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