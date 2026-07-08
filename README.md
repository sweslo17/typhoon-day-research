# Typhoon Day Research

Reproducible research package for Taiwan typhoon-day decisions, election timing, official forecast-vs-observed weather, an interpretable prediction method, and Medium-style statistical science drafts.

Primary workflow:

```bash
PYTHONPATH=src python3 -m typhoon_day_research.cli run-sample
PYTHONPATH=src python3 -m unittest discover -s tests
```

Autopilot workflow, following A, C, B:

```bash
# A. Fetch and build the research dataset.
PYTHONPATH=src python3 -m typhoon_day_research.cli fetch-dgpa --raw-dir data/raw/dgpa --pages 49
PYTHONPATH=src python3 -m typhoon_day_research.cli build-dataset --raw-dir data/raw/dgpa --out data/processed/dgpa_decisions.csv
PYTHONPATH=src python3 -m typhoon_day_research.cli analyze --decisions-csv data/processed/dgpa_decisions.csv --out-dir reports/analysis

# C. Parse CWA forecast data and run interpretable probability scenarios.
PYTHONPATH=src python3 -m typhoon_day_research.cli parse-wpps --input data/raw/cwa/WPPS-Data.js --out data/processed/cwa_wpps_forecast.csv
PYTHONPATH=src python3 -m typhoon_day_research.cli predict-batch --input data/manual/taipei_typhoon_week_scenario.csv --out reports/generated/prediction_week_taipei.json

# B. Render Medium drafts.
PYTHONPATH=src python3 -m typhoon_day_research.cli drafts --out-dir reports/medium
```

See `docs/research_brief.md` for source notes, legal criteria, election-timing assumptions, and the article series plan.

Published-writing package:

- Complete Medium-ready article series: `reports/articles/`
- Earlier short drafts: `reports/medium/`
- Analysis figures and tables: `reports/analysis/`
- Weekly prediction example: `reports/generated/prediction_week_taipei.json`
