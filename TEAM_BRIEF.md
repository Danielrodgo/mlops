# Team brief

## Business and data
- Business case: README.md, section 1 (merged into dev on 2026-11-04)
- Use case: Operations Planning decides the number of field crew per shift for the following day, using the hourly demand forecast; the plan is assumed to be made at 18:00 the previous evening (README, Solution)
- Notebook: notebooks/bike_demand_forecast.ipynb
- Target: cnt | Problem type: regression | ID column: ts (built from dteday and hr in clean_data, kept out of features)

## Features, model and evaluation
- Feature groups: calendar: hr, weekday, mnth, season -> passthrough (integer codes, trees split on them directly)
- Feature groups: flags: holiday, workingday -> passthrough (already 0 or 1)
- Feature groups: history: lag_30, lag_31, lag_48, lag_168, roll_mean_24, roll_mean_168 -> passthrough (built in clean_dataframe by a fixed rule, nothing is fitted)
- Excluded columns: casual, registered (together equal the target), weathersit, temp, atemp, hum, windspeed (same-hour weather is unknown at prediction time), instant, dteday, yr (not used in the notebook), is_imputed (inspection flag only)
- Model: HistGradientBoostingRegressor, loss="quantile", quantile=2/3 (under_weight 2 / (1 + 2)), learning_rate=0.05, max_iter=622, max_leaf_nodes=31, min_samples_leaf=40, early_stopping=False
- Metric: weighted_mae (weight 2 when prediction < actual, else 1), key in evaluate_model output: ["weighted_mae"], quality gate: <= 0.85 x baseline, about 211 (provisional, re-measured when the pipeline runs; replaces 211.75). evaluate_model also returns "mae" and "under_share"
- Split: chronological, no shuffle, test 0.127 and validation 0.127 of the full dataset; random_state 42

## Rules, decisions and ownership
- Validation rules: expected columns; no missing values; no duplicate timestamps; hr in 0..23 (stop bad data before training); cnt >= 0 and cnt = casual + registered, training mode only; inference input has at least about 200 h of history
- README follow-ups: amendments 1 to 6 done (day-ahead crew planning). The business KPI baseline stays "To be measured".
- features.py signature: get_feature_preprocessor(calendar_columns, flag_columns, history_columns), settings per group: none (all passthrough, remainder dropped)
- Agreed extra parameters: split_data(..., chronological=False); clean_dataframe(..., lag_hours=[30, 31, 48, 168], rolling_windows=[24, 168], rolling_shift=30); validate_dataframe(..., min_target=None)
- utils.py helpers: load_csv, save_csv, save_model, load_model
- Environment: none beyond pandas, numpy, scikit-learn, joblib, pytest, flake8 (matplotlib stays in the notebook)
- Decisions: lags and rolling means built in clean_dataframe by a fixed row-order rule, inference input carries the history (same features in training and inference); missing hours zero-filled in training mode only (inference adds no rows); max_iter fixed at 622 (found with the notebook's 2-hour lag; to be re-checked once on the 30 h inputs before it is frozen), no round search in the pipeline; model trained on the train split, gate scored on validation, test sealed until an approved final audit
- Horizon: the forecast is made at 18:00 for each hour of the following day (worst case about 30 h ahead), so every history input is at least 30 h old
- Owners (solo): all modules -> Daniel