# Cover Performance Analytics

A bilingual Streamlit application that turns cover-song performance data into deterministic analytics and grounded, actionable creator recommendations.

## Quick Links

- Demo Video: Coming soon
- Devpost Submission: Coming soon
- Build Week branch: `feature/build-week-ai`
- [Installation](#installation)
- [Tests](#tests)

## OpenAI Build Week Submission

### Problem

Music creators can collect views, likes, comments, saves, and shares from social platforms, but those numbers do not automatically answer the next practical question: what should they test or publish next? Small samples and unusually high rate metrics can also make an apparently strong result less reliable than it first appears.

### Solution

Cover Performance Analytics combines deterministic Python analytics with an AI Creator Coach. Python calculates and summarizes the evidence first; GPT-5.6 Sol then interprets only that bounded context and returns a structured, bilingual report with strengths, risks, recommended actions, a next-cover strategy, and explicit data limitations.

### What Was Added During Build Week

The AI Creator Coach extends the completed V3 application without changing its CSV persistence model or existing analytics features.

#### Pre-existing V3 foundation

- Streamlit dashboard
- Centralized CSV-based data access
- Cover and metric snapshot tracking
- Growth and pattern analytics
- Candidate testing and candidate history
- Turkish and English internationalization
- CSV and localized text report export

#### Build Week additions

- Deterministic, compact AI context builder
- Evidence-quality warnings for low-view outliers
- Strict AI report JSON Schema and local validator
- GPT-5.6 Sol integration through the OpenAI Responses API
- Strict Structured Outputs
- Bilingual AI Creator Coach interface
- Session-state caching and stale-report detection
- Safe API, validation, configuration, and secret handling
- Focused standard-library unit-test coverage

### Why GPT-5.6 Sol

GPT-5.6 Sol interprets bounded evidence; it does not calculate the portfolio metrics. All metrics and rankings are prepared deterministically in Python before a request is made.

The service prompt and response contract require the model to:

- base recommendations only on the supplied context;
- avoid inventing metrics or unsupported facts;
- describe directional relationships without claiming causation;
- respect each cover's `evidence_quality` and `evidence_flags`; and
- treat `low_view_sample` as low-confidence evidence rather than a conclusive result.

### How Codex Was Used

Codex supported the Build Week work as an implementation and review partner. It:

- performed a read-only architecture review before implementation;
- inspected the existing repository and followed its established conventions;
- implemented the feature as small, independently testable components;
- created and extended focused unit tests;
- ran compile, diff, and full regression checks;
- supported iterative human review and targeted repair; and
- did not receive, inspect, store, or expose the OpenAI API key.

### Validation Status

- 63 unit tests passing
- Python compile check passing
- Turkish and English real API smoke tests passing
- Cache and stale-report behavior manually verified
- No automatic or background API calls

### Architecture

```text
CSV data
    |
    v
calculate_metrics()
    |
    v
build_ai_creator_context()
    |
    v
GPT-5.6 Sol Responses API
    |
    v
Strict Structured Output
    |
    v
validate_ai_creator_report()
    |
    v
Streamlit AI Creator Coach
```

The deterministic context contains compact portfolio totals and averages, medians, top-cover evidence, category comparisons, and stable data-quality codes. The model response is accepted only after it passes the local contract validator.

#### Key technical files

| File | Responsibility |
| --- | --- |
| `src/ai_context_builder.py` | Builds a pure, deterministic, JSON-compatible analytics context and flags low-view evidence. |
| `src/ai_report_contract.py` | Defines the strict report JSON Schema and validates model output locally. |
| `src/ai_creator_service.py` | Creates the bounded GPT-5.6 Sol Responses API request and maps configuration, request, and response failures to safe errors. |
| `src/ui/ai_creator_coach_section.py` | Handles explicit generation, bilingual rendering, session caching, stale-report detection, and safe user feedback. |

#### Project structure

```text
cover-performance-analytics/
|-- app.py
|-- requirements.txt
|-- data/
|   |-- covers.csv
|   |-- metrics_snapshots.csv
|   `-- candidate_tests.csv
|-- src/
|   |-- analyzer.py
|   |-- ai_context_builder.py
|   |-- ai_creator_service.py
|   |-- ai_report_contract.py
|   |-- candidate_history_analyzer.py
|   |-- candidate_test_repository.py
|   |-- data_manager.py
|   |-- i18n.py
|   |-- opportunity_analyzer.py
|   |-- pattern_analyzer.py
|   `-- ui/
|       |-- ai_creator_coach_section.py
|       |-- candidate_history_section.py
|       |-- filter_section.py
|       |-- growth_section.py
|       |-- main_dashboard_section.py
|       |-- pattern_section.py
|       |-- report_export_section.py
|       `-- sidebar_section.py
`-- tests/
    |-- test_ai_context_builder.py
    |-- test_ai_creator_coach_section.py
    |-- test_ai_creator_service.py
    `-- test_ai_report_contract.py
```

### Technology Stack

- Python 3.12
- Streamlit
- pandas
- OpenAI Python SDK
- GPT-5.6 Sol
- `unittest`
- CSV-based data storage
- Git and GitHub

### Safety and Cost Controls

- API calls occur only after an explicit Generate or Regenerate button click.
- Validated reports are cached in session state and survive ordinary Streamlit reruns.
- Cached reports become stale and are hidden when the language, filters, source data, or configured model changes.
- The API key is read at runtime from an ignored Streamlit secrets file.
- Secrets are never stored in session state or included in the AI context.
- Missing keys, insufficient data, invalid model output, and API failures are handled separately.
- There are no automatic retries, background requests, or calls triggered by normal reruns.

## Installation

Clone the verified public repository and enter the project directory:

```powershell
git clone https://github.com/Barandlnn/cover-performance-analytics.git
cd cover-performance-analytics
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` locally and add only your own project key:

```toml
OPENAI_API_KEY = "your-project-api-key"
```

Never commit a real API key. The repository ignores `.streamlit/secrets.toml`, and the application handles a missing key without making an API request.

## Running the Application

Run the application through the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Tests

Run the complete unit-test suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Compile the application and tests:

```powershell
.\.venv\Scripts\python.exe -m compileall app.py src tests
```

### Three-Minute Demo Flow

1. Open the dashboard and briefly show the existing English/Turkish interface and filters.
2. Show the deterministic portfolio metrics, rankings, growth, and pattern analytics.
3. Open the AI Creator Coach section and show the compact local data scope.
4. Explain the `evidence_quality` warning for rate outliers backed by unusually low views.
5. Click Generate once and review the structured strengths, risks, actions, strategy, and limitations.
6. Switch language or filters to demonstrate bilingual output, session caching, and stale-report protection.

### Build Week Commit History

The feature was delivered as four small, independently testable commits:

1. `Add deterministic AI context builder`
2. `Add structured AI report contract`
3. `Add OpenAI creator report service`
4. `Add AI Creator Coach interface`

### Current Limitations

- The current demo dataset is small.
- Persistence remains CSV-based for this Build Week scope.
- Insights are directional and do not establish causation.
- Broader confidence requires more covers, comparable observations, and repeated tests.

### Future Roadmap

- Migrate persistence to SQLite or PostgreSQL.
- Add platform API and ETL-based data ingestion.
- Expand caption, hashtag, and posting-time analytics.
- Add anomaly and trend detection.
- Evaluate recommendation quality at a larger scale with repeated outcomes.
- Continue broader ML/LLM work such as prediction, learned scoring, and suggestion evaluation.

The grounded AI Creator Coach is complete for Build Week. It is one completed part of the V6 direction; broader V6 machine-learning and LLM functionality remains planned or in progress.

## Legacy V3 Product Documentation

The sections below preserve the detailed documentation for the V3 product foundation on which the Build Week feature was built.

### Overview

Cover Performance Analytics was created to support data-driven decisions for cover-song content production.

Instead of selecting songs only through intuition, the application records cover metadata and performance snapshots, calculates analytics metrics, identifies recurring patterns, and evaluates potential future cover ideas.

The V3 application supports:

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
- CSV and localized text report export

### V3 Features

#### Bilingual User Interface

The selected language affects headings, form labels, validation messages, table columns, insights, recommendations, candidate labels, and explanations. Internal calculations and stored CSV values remain in a consistent canonical format.

#### Cover Management and Metric Snapshots

Cover records include song, artist, platform, content type, genre, publishing details, hook and vocal styles, recording and arrangement types, mood, and production scores.

Time-based snapshots store views, likes, comments, saves, and shares. Multiple snapshots can belong to one cover, allowing growth tracking without overwriting earlier observations. Newly entered cumulative metrics cannot be lower than the latest recorded values.

#### Main Dashboard and Analytics

The filterable dashboard calculates performance score, engagement rate, save rate, share rate, comment rate, rankings, and dynamic insights. Growth analytics compares snapshots, while pattern analytics evaluates recurring content characteristics and produces confidence-aware summaries and planning recommendations.

#### Candidate Testing and History

Users can score future cover ideas from selected attributes, review classifications and supporting explanations, and save results. Candidate history provides summary metrics, dynamic insights, top tests, genre comparisons, and score charts.

#### Report Export

Filtered dashboard data can be exported as UTF-8 CSV or as a localized Turkish or English text summary without modifying source data. The text report includes portfolio metrics, the best-performing cover, dynamic insights, and its generation time.

### V3 Architecture

- `app.py` composes the application, language selection, data loading, analysis, and UI sections.
- `src/data_manager.py` centralizes CSV paths and data access.
- Analysis modules contain calculations and business logic.
- Files under `src/ui/` own Streamlit presentation and interaction.
- `src/i18n.py` contains English and Turkish translations and helpers.

### Data Model

- `covers.csv` stores stable cover metadata.
- `metrics_snapshots.csv` stores time-dependent performance metrics; multiple snapshots can belong to one cover.
- `candidate_tests.csv` stores historical candidate-cover test results.

### Typical V3 Workflow

1. Add a cover and its metadata.
2. Record the first performance snapshot.
3. Add later snapshots as cumulative metrics increase.
4. Filter and inspect dashboard results.
5. Review growth and pattern analytics.
6. Test and save future cover candidates.
7. Compare candidate history and export a report.

### V3 Status and Roadmap Context

V3 productization is complete, including modular UI sections, centralized CSV access, bilingual analytics, candidate testing and history, documentation, and report export.

The original roadmap continues with data-infrastructure work, advanced analytics, and broader ML/LLM features. The Build Week AI Creator Coach completes a grounded recommendation component while leaving the broader roadmap explicitly unfinished.

### Project Goal

The long-term goal is to evolve the application from a manually managed analytics dashboard into a data-driven content decision system that can support multiple social media platforms and predictive analytics.

## Türkçe Özet

Cover Performance Analytics, cover şarkı içeriklerinin performansını takip etmek ve gelecek içerik kararlarını veriye dayalı hale getirmek amacıyla geliştirilmiş bir Streamlit uygulamasıdır.

Uygulama; cover bilgilerini ve zaman bazlı metrikleri kaydeder, performans ve büyüme analizleri üretir, başarılı içerik kalıplarını inceler ve yeni cover adaylarını skorlayarak öneriler oluşturur.

Arayüz tamamen Türkçe ve İngilizce çalışmaktadır. Hesaplama ve kayıt değerleri tutarlı bir dahili formatta korunurken kullanıcıya gösterilen metinler seçilen dile göre çevrilir.
