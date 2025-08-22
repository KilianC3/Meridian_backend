# Operational Runbook

## Risk engine

- Recompute risk metrics manually:

  ```bash
  python -m app.scheduler.jobs.risk_metrics
  ```

- Launch the scheduler to keep metrics fresh:

  ```bash
  python -m ingestion.scheduler.run
  ```

  This reads `ingestion/registry/datasets.yaml` and schedules each enabled
  dataset according to its `cadence`.

## Adding a dataset

1. Register the dataset in `ingestion/registry/datasets.yaml` with its adapter
   path, transform, target table and cadence.
2. Implement the adapter class exposing a `run` method that yields raw records.
3. Optionally create a transform function to map raw records into table rows.
4. Run `make migrate` if new tables are required and restart the scheduler.

## Backfilling

Backfill historical data for a dataset over a given window:

```bash
python -m ingestion.scheduler.backfill --dataset DATASET_ID --start YYYY-MM-DD --end YYYY-MM-DD
```

## Health checks

- `/healthz` – liveness probe.
- `/readiness` – verifies DB connectivity and dataset freshness.

## Metrics and logs

- Application metrics are exposed at `/metrics` for Prometheus.
- Scheduler logs and job outcomes are available via `docker compose logs`.

