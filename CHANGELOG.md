# Changelog — Separation of Concerns Refactor

All notable changes from the recent refactor are listed below. The goal was
to separate UI, services, model, presentation, and utilities to improve
testability and maintainability while preserving existing behavior.

## Unreleased

- Introduced `controller/WeatherService` and `controller/AppController` to
  encapsulate network I/O and application orchestration.
- Moved UI-facing helpers into `view/ui_helpers.py` and added shims in
  `utils/` to preserve existing APIs.
- Hardened network error handling in `utils/web_utils.py`.
- Centralized station filtering in `model/helpers.py`.
- Moved weather calculations to `model/physics.py` and delegated calls from
  `utils/weather_utils.py`.
- Added a background `NetworkWorker` (`view/background_worker.py`) and wired
  the UI (`pyweatherview.py`) to use it to avoid blocking the main thread.
- Added `scripts/smoke_test.py` for automated programmatic checks.

### Files added

- `controller/weather_service.py`
- `controller/app_controller.py`
- `controller/__init__.py`
- `view/ui_helpers.py`
- `view/background_worker.py`
- `model/helpers.py`
- `model/physics.py`
- `scripts/smoke_test.py`

### Files modified

- `pyweatherview.py` (now uses `AppController`, background worker)
- `utils/utils.py` (shims to `view/ui_helpers`)
- `utils/weather_utils.py` (presentation shims, delegates calculations)
- `utils/web_utils.py` (improved error handling)
- `model/weather_station.py`, `model/station_info.py`, `model/data_model.py`

## Suggested branch and commit strategy

- Branch: `refactor/separation-of-concerns`
- Create small commits per task (see `scripts/create_branch_and_commit.ps1`).
