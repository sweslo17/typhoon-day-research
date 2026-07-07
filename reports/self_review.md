# Self Review

## Verification Evidence

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 15 tests passed.
- `python3 -m compileall -q src tests`: exit 0.
- DGPA full fetch: 49 history pages, 481 notices, 481 detail pages, 822 attachments.
- DGPA processed dataset: 5,220 decision rows from 2001-07-30 through 2026-06-28.
- CWA WPPS current forecast parse: 24 rows from `WPPS-Data.js`.

## Issues Found During Review

- Fixed a DGPA classification bug where `未達停止上班及上課標準` was incorrectly counted as stopped because it contains the substring `停止上班`.
- Fixed a WPPS parsing bug where HTML entity semicolons, such as `&nbsp;`, prematurely ended JavaScript assignment parsing.
- Added explicit election timing groups for same-year and next-year presidential/local elections. Groups are non-exclusive.

## Current Limitations

- The prediction model is a transparent baseline, not a fitted causal model.
- DGPA county normalization preserves pre-2010 county forms as separate labels to avoid silently rewriting history.
- CWA forecast areas include sub-county regions such as `恆春半島` and `蘭嶼綠島`; future forecast-vs-decision joins need a mapping table.
- CODiS observation fetching is implemented as a source client, but a full historical forecast-vs-observed matched panel is not yet generated.
