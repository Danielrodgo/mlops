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

Baseline: a historical-average rule (average demand for the same weekday and hour, using only data before the period being scored), scored on the validation period, in rentals per hour. Source: `hour.csv`. Value: about 249 rentals per hour of `weighted_mae` (provisional), to be fixed when the pipeline measures it.

### Goal and success metrics
Business KPI: idle field crew hours per week, in hours, baseline To be measured, source: the client's shift rosters and rental logs (not in this dataset). The target is to be set once the baseline is measured.

ML metric: `weighted_mae` in rentals per hour, used for both the baseline and the model, with plain `mae` reported next to it. An hour's absolute error counts twice when the forecast is below actual demand and once otherwise. Lower is better. The release gate is scored on the validation period, and the test period stays sealed until an approved final audit. Release threshold: `weighted_mae_model <= 0.85 * weighted_mae_baseline`, about 211 rentals per hour (provisional, fixed in the pipeline settings).

| Business KPI | Idle field crew hours per week | To be measured | To be set once the baseline is measured |
| ML metric | `weighted_mae` (rentals per hour) | About 249 (provisional) | <= 0.85 x baseline, about 211 (15% better, assumption) |
| Limit | Prediction response time | n/a | Under 1 s at p95 |
| Limit | Inference cost | n/a | Under EUR 0.01 per prediction (initial estimate) |

Link: more accurate hourly forecasts, especially avoiding under-estimates, can help planners set the number of field crew per shift better. The real reduction in idle crew hours must be validated in the pilot.

Release criteria: no promotion to production unless the model beats the baseline by at least 15% on the validation period, meets the latency and cost limits, and passes data quality and leakage checks.

### Solution
Operations Planning uses the system-wide hourly demand forecast to decide the number of field crew members assigned to each shift for the following day, with the plan assumed to be made at 18:00 the previous evening. The Operations Manager stays responsible for all final decisions. The model gives estimates and does not assign field crew automatically.

The model predicts total rentals (`cnt`) for each hour of the following day, using hour of day, weekday, month, season, holiday status, working-day status and past rental demand from at least 30 hours before the hour being forecast. Weather variables are excluded at first because the actual weather for the forecast hours is not known at prediction time. Weather forecasts could be added later. `casual` and `registered` are excluded because together they determine the target.

Serving: one batch run per day at 18:00, producing a forecast for each of the 24 hours of the following day.

Fallback: if the model is unavailable, returns invalid results or fails reliability checks, the system uses the historical-average rule. Planners can also use historical reports and experience.

Scope: the first version forecasts system-wide hourly demand. Station-level recommendations need station-level data.

### Data
Source: UCI Bike Sharing Dataset (`hour.csv`), created by Hadi Fanaee-T and distributed through the UCI Machine Learning Repository. The rental data originates from Capital Bikeshare. Licence: CC BY 4.0.

Size: 17,379 hourly rows, January 2011 to December 2012. Other references list a different row count.

Label: `cnt` is the hourly total of casual and registered rentals, known only after the hour ends.

Refresh: the UCI file is a fixed snapshot. In the scenario, we assume the rental system supplies aggregated hourly records, and a Data Engineering team owns ingestion, validation and versioning.

Inputs: calendar variables and past rental counts from at least 30 hours before each forecast hour: the counts 30, 31, 48 and 168 hours earlier, and the averages of the previous 24 and 168 hours ending 30 hours earlier. The pipeline needs about 200 hours of history. Same-hour weather, `casual`, `registered` and same-hour `cnt` are excluded to avoid leakage.

Personal data: none. The data is aggregated hourly counts with no customer identifiers. Production access would still need security and governance controls.

### Value, cost and risks
Benefit over a non-AI approach: at least 15% lower `weighted_mae` than the historical-average rule. Gains in idle field crew hours must be validated in the pilot with the client's shift roster data.

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
- Business KPI baseline (idle field crew hours per week): To be measured (needs the client's shift rosters and rental logs).
- Baseline value of the historical-average rule: about 249 `weighted_mae` on validation (provisional); the exact value is fixed when the pipeline measures it.
- The 2x penalty, the 15% improvement threshold and the 18:00 planning time are assumptions to validate with the client.
- Data delay: rentals up to 17:00 are assumed to be recorded by 18:00. This is an assumption to validate with the client.- Missing hours: 17,379 rows against 17,544 expected for a complete record; handling not yet defined.
- Risks: no freshness check or last-resort step if the data feed fails (it would break both model and fallback), and the drift mitigation names no comparison or retraining trigger.