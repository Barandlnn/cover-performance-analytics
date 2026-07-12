# Cover Performance Analytics

A bilingual Streamlit analytics application for tracking, evaluating, and comparing the performance of cover-song content.

The project analyzes manually entered social media performance data, identifies growth and content patterns, and helps evaluate future cover-song candidates.

## Overview

Cover Performance Analytics was created to support data-driven decisions for cover-song content production.

Instead of selecting songs only through intuition, the application records cover metadata and performance snapshots, calculates analytics metrics, identifies recurring patterns, and evaluates potential future cover ideas.

The application currently supports:

- English and Turkish user interfaces
- Cover metadata management
- Time-based metric snapshots
- Performance and engagement analytics
- Growth analytics
- Pattern discovery
- Rule-based insight generation
- Cover planning recommendations
- Candidate cover scoring
- Candidate test history analytics

## Features

### Bilingual User Interface

The complete application interface supports:

- English
- Turkish

The selected language affects headings, form labels, validation messages, table columns, insights, recommendations, candidate labels, and explanations.

Internal calculation values and stored CSV values remain in a consistent canonical format.

### Cover Management

New cover records can be added with metadata such as:

- Song title
- Artist
- Platform
- Content type
- Genre
- Post date and time
- Duration
- Hook type
- Vocal style
- Recording type
- Arrangement type
- Song mood
- Audio and thumbnail scores

### Metric Snapshots

Performance metrics are stored as time-based snapshots:

- Views
- Likes
- Comments
- Saves
- Shares

The snapshot structure makes it possible to track performance changes over time instead of overwriting previous values.

The application also prevents newly entered cumulative metrics from being lower than the latest recorded values.

### Main Performance Dashboard

The main dashboard provides:

- Filterable cover performance data
- Performance score calculations
- Engagement rate
- Save rate
- Share rate
- Comment rate
- Top-performing covers
- Dynamic performance insights

### Growth Analytics

Growth analytics compares multiple snapshots belonging to the same cover.

It calculates metrics such as:

- Views growth
- Likes growth
- Engagement growth
- Snapshot count
- First and latest snapshot dates
- Growth rates

### Pattern Analytics

Pattern analytics evaluates recurring characteristics of successful cover content.

Analyzed dimensions include content-related attributes such as:

- Genre
- Artist
- Content type
- Hook type
- Vocal style
- Recording type
- Arrangement type
- Song mood

The system produces:

- Pattern summaries
- Confidence-weighted pattern scores
- Dynamic insights
- Cover planning recommendations

### Candidate Cover Test

Users can test a future cover idea by selecting candidate attributes.

The system generates:

- Candidate score
- Candidate classification
- Recommended action
- Supporting explanations
- Data-confidence warnings

Candidate results can be saved for later comparison.

### Candidate History Analytics

Saved candidate tests are analyzed through:

- Candidate history table
- Summary metrics
- Dynamic history insights
- Top candidate tests
- Genre-based candidate performance
- Candidate score charts

## Technology Stack

- Python
- Streamlit
- pandas
- CSV-based data storage
- Git and GitHub

## Project Structure

```text
cover-performance-analytics/
│
├── app.py
├── requirements.txt
│
├── data/
│   ├── covers.csv
│   ├── metrics_snapshots.csv
│   └── candidate_tests.csv
│
└── src/
    ├── analyzer.py
    ├── candidate_history_analyzer.py
    ├── candidate_test_repository.py
    ├── data_manager.py
    ├── i18n.py
    ├── opportunity_analyzer.py
    ├── pattern_analyzer.py
    │
    └── ui/
        ├── candidate_history_section.py
        ├── filter_section.py
        ├── growth_section.py
        ├── main_dashboard_section.py
        ├── pattern_section.py
        └── sidebar_section.py
```

## Architecture

The project follows a modular structure with separated responsibilities.

### `app.py`

Acts as the application composition layer.

It:

- Configures Streamlit
- Manages language selection
- Loads application data
- Calls analysis functions
- Composes the UI sections

### `src/data_manager.py`

Centralizes CSV paths and data access.

UI and analysis modules do not directly read from or write to CSV files.

### Analysis Modules

Analysis modules contain calculation and business logic:

- `analyzer.py`
- `pattern_analyzer.py`
- `candidate_history_analyzer.py`
- `opportunity_analyzer.py`

### UI Modules

Files under `src/ui/` manage Streamlit presentation and user interaction.

They do not own CSV paths or core calculation logic.

### `src/i18n.py`

Contains the Turkish and English translation dictionaries and translation helpers.

## Data Model

### `covers.csv`

Stores stable cover metadata.

Examples:

- Cover ID
- Title
- Artist
- Platform
- Genre
- Content characteristics
- Recording characteristics

### `metrics_snapshots.csv`

Stores time-dependent performance metrics.

Multiple snapshots can belong to the same cover.

### `candidate_tests.csv`

Stores historical candidate cover test results.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/Barandlnn/cover-performance-analytics.git
cd cover-performance-analytics
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Running the Application

Always run the application through the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will display the local application URL in the terminal.

## Typical Workflow

1. Add a new cover and its metadata.
2. Add the first performance snapshot.
3. Add new snapshots as metrics increase.
4. Filter and inspect dashboard results.
5. Review growth analytics.
6. Examine content patterns and recommendations.
7. Test future cover candidates.
8. Save candidate results.
9. Compare candidate history analytics.

## Current Project Status

The project is currently in the **V3 Productization** phase.

Completed areas include:

- Modular UI refactor
- Centralized data access
- Dashboard and analytics separation
- Turkish and English language support
- Candidate analytics architecture

## Roadmap

### V3 — Productization

- Dashboard and UI refactor
- Turkish and English language support
- Project documentation
- Report export
- Final productization checks

### V4 — Data Infrastructure

- SQLite or PostgreSQL migration
- Database-backed persistence
- ETL preparation
- Instagram API-compatible data model

### V5 — Advanced Analytics

- Caption analysis
- Hashtag analysis
- Posting-time analysis
- Anomaly detection
- Trend comparison

### V6 — Machine Learning and LLM Features

- Performance prediction
- Learned candidate scoring
- Caption and hashtag suggestions
- Trending-song matching
- AI-assisted content recommendations

## Project Goal

The long-term goal is to evolve this application from a manually managed analytics dashboard into a data-driven content decision system that can support multiple social media platforms and predictive analytics.

## Türkçe Özet

Cover Performance Analytics, cover şarkı içeriklerinin performansını takip etmek ve gelecek içerik kararlarını veriye dayalı hale getirmek amacıyla geliştirilmiş bir Streamlit uygulamasıdır.

Uygulama; cover bilgilerini ve zaman bazlı metrikleri kaydeder, performans ve büyüme analizleri üretir, başarılı içerik kalıplarını inceler ve yeni cover adaylarını skorlayarak öneriler oluşturur.

Arayüz tamamen Türkçe ve İngilizce çalışmaktadır. Hesaplama ve kayıt değerleri tutarlı bir dahili formatta korunurken kullanıcıya gösterilen metinler seçilen dile göre çevrilir.
