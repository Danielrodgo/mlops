# Hourly Bike Rental Demand Forecasting

> Capital Bikeshare should invest in an MLOps demand forecasting system because automated testing, monitoring, and retraining detect issues and support recovery, unlike one-off notebooks.

## 1. Business case

### Context
Client: Capital Bikeshare, Operations Planning and Fleet Management business unit. This is a hypothetical scenario built on the public UCI Bike Sharing Dataset (`hour.csv`). It does not describe the company's actual technology, processes, organisation or forecasting capabilities.

Maturity:
- Data: Medium. 17,379 consistently structured hourly observations (2011 to 2012) with rental counts, weather, calendar and seasonal variables, and no reported missing values. The client's real data infrastructure and governance are not verified.
- Technology: Low (assumed). We start from CSV data and build the ML infrastructure in this project.
- Process: Low (assumed). Automated monitoring and retraining do not exist in this scenario.
- People: Medium (assumed). Operations and technical specialists collaborate.

Ownership: Operations Planning owns the business use of the predictions. Data Engineering / ML Engineering owns the technical system (deployment, monitoring, retraining).

### Problem and baseline
The Operations Planning and Fleet Management team struggles with potential bicycle shortages in high-demand periods because demand varies with weather, time of day, weekday and season. Too many bicycles in low-demand locations also create unnecessary rebalancing costs.

The team is assumed to plan distribution from historical reports and operational experience. This process is not verified as Capital Bikeshare's real procedure.

Baseline: a historical-average rule (average demand for the same weekday and hour, using only data before the test period), scored on a chronological test period, in rentals per hour. Source: `hour.csv`. Value: To be measured.

### Goal and success metrics
Business KPI: raise the bicycle availability rate (share of station-hours with at least one bicycle) by 5 percentage points within six months of the operational pilot. The baseline is unknown and needs station-level data. The target is an assumption to validate with the client.

ML metric: `weighted_mae` in rentals per hour on unseen chronological test data, penalising under-prediction twice as much as over-prediction. Lower is better. Release threshold: `weighted_mae_model <= 0.85 * weighted_mae_baseline`.

| Type | Metric (exact name) | Baseline | Target or threshold |
| --- | --- | --- | --- |
| Business KPI | Bicycle availability rate | To be measured | +5 percentage points (assumption) |
| ML metric | `weighted_mae` (rentals per hour) | To be measured | <= 0.85 x baseline (15% better, assumption) |
| Limit | Prediction response time | n/a | Under 1 s at p95 |
| Limit | Inference cost | n/a | Under EUR 0.01 per prediction (initial estimate) |

Link: more accurate hourly forecasts, especially avoiding under-estimates, can help planners allocate bicycles better. The real availability gain must be validated in the pilot.

Release criteria: no promotion to production unless the model beats the baseline by at least 15%, meets the latency and cost limits, and passes data quality and leakage checks.

### Solution
The Operations Planning and Fleet Management team receives hourly demand forecasts to support bicycle distribution and resource planning. The Operations Manager stays responsible for all final decisions. The model gives estimates and does not redistribute bicycles automatically.

The model predicts total rentals (`cnt`) for the upcoming hour using hour of day, weekday, month, season, holiday status, working-day status and historical rental demand. Weather variables are excluded at first because the weather for the upcoming hour is not known at prediction time. Weather forecasts could be added later. `casual` and `registered` are excluded because together they determine the target.

Serving: hourly batch predictions, generated shortly before each new hour.

Fallback: if the model is unavailable, returns invalid results or fails reliability checks, the system uses the historical-average rule. Planners can also use historical reports and experience.

Scope: the first version forecasts system-wide hourly demand. Station-level recommendations need station-level data.

### Data
Source: UCI Bike Sharing Dataset (`hour.csv`), created by Hadi Fanaee-T and distributed through the UCI Machine Learning Repository. The rental data originates from Capital Bikeshare. Licence: CC BY 4.0.

Size: 17,379 hourly rows, January 2011 to December 2012. Other references list a different row count.

Label: `cnt` is the hourly total of casual and registered rentals, known only after the hour ends.

Refresh: the UCI file is a fixed snapshot. In the scenario, we assume the rental system supplies aggregated hourly records, and a Data Engineering team owns ingestion, validation and versioning.

Inputs: calendar variables and historical rental counts from completed hours. Same-hour weather, `casual`, `registered` and same-hour `cnt` are excluded to avoid leakage.

Personal data: none. The data is aggregated hourly counts with no customer identifiers. Production access would still need security and governance controls.

### Value, cost and risks
Benefit over a non-AI approach: at least 15% lower `weighted_mae` than the historical-average rule. Availability and rebalancing cost gains must be validated in the pilot with station-level data.

Rough cost (illustrative estimates, excluding salaries and existing infrastructure):
- People: one Data Scientist / ML Engineer full time, one Data Engineer part time, one Operations representative part time
- Infrastructure: EUR 20 to 100 per month
- Time: 6 to 8 weeks for development, testing and first release, including pilot preparation. The six-month pilot is separate.

Scales to: station-level forecasting, electric scooter fleets, public transport capacity planning, and other bike-sharing operators or cities, reusing the MLOps architecture with new data and validation.

Limitation: training data covers 2011 to 2012, so recent operational data is needed before production.

| Risk | Mitigation |
| --- | --- |
| Data quality issues, missing observations, inconsistent records | Automated schema validation, missing-value checks, duplicate detection |
| Incorrect predictions causing shortages | Monitor `weighted_mae` and under-prediction frequency, alert on deterioration, require human approval of redistribution, switch to the historical-average rule if reliability thresholds are breached |
| Performance decline from changing demand patterns | Monitor data and model drift, define retraining triggers, evaluate periodically on recent data |
| Model or API unavailability | Health checks, historical-average fallback, model rollback |
| Unauthorised access or misuse | API authentication, role-based access control, logging of operational decisions |

### Open gaps
- Availability rate baseline: To be measured (needs station-level data).
- Baseline value of the historical-average rule: To be measured.
- Metric mismatch: choose one metric (plain MAE or `weighted_mae`) for baseline and model, with a precise definition.
- The 5 percentage point target, 2x penalty and 15% threshold are assumptions to validate with the client.
- Test period start date not yet named.
- Input definition: which past `cnt` values, how far back, and when the latest is available.
- Missing hours: 17,379 rows against 17,544 expected for a complete record; handling not yet defined.
- Risks: no freshness check or last-resort step if the data feed fails (it would break both model and fallback), and the drift mitigation names no comparison or retraining trigger.