# Meridian Backend

FastAPI service providing analytics capabilities with supporting infrastructure.

## Development

```bash
poetry install
cp .env.example .env
pre-commit install
make up  # start local Postgres, Mongo, Redis and the API
```

The API will be available at [http://localhost:8000](http://localhost:8000). Format, lint and test with:

```bash
make fmt
make lint
make test
```

Stop the stack with `make down`.

## Production

Build and run the service using Docker Compose and the production override file:

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

To manage the service via systemd:

```bash
sudo cp infra/systemd/meridian.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now meridian
```

Configuration is read from `/etc/meridian/.env`.

## Environment Variables

| Variable | Description |
| -------- | ----------- |
| `APP_NAME` | Application name used for logging |
| `ENV` | Environment identifier (`development`, `production`, etc.) |
| `VERSION` | Application version string |
| `GIT_SHA` | Git commit SHA for the build |
| `BUILD_TIME` | ISO8601 timestamp when the build was created |
| `POSTGRES_DSN` | PostgreSQL connection string |
| `MONGO_DSN` | MongoDB connection string |
| `REDIS_DSN` | Redis connection string |
| `SECRET_KEY` | Secret key for signing tokens |
| `SENTRY_DSN` | Optional Sentry DSN for error tracking |
| `PING_TIMEOUT` | Timeout in seconds for dependency health checks |
| `READINESS_CACHE_TTL` | TTL in seconds for cached readiness results |
| `CORS_ORIGINS` | Comma separated list of allowed CORS origins |
| `RISK_WINDOW_DAYS` | Rolling window size for EWMA volatility |
| `MAX_LAG_DAYS` | Maximum lag search window for factor connections |
| `DEFAULT_SHOCK_SIGMA` | Default shock size for simulations |
| `VECTOR_STORE_URL` | Optional vector store endpoint for evidence embeddings |
| `VECTOR_STORE_API_KEY` | API key for the vector store |
| `FRED_API_KEY` | API key for Federal Reserve Economic Data |
| `EIA_API_KEY` | API key for U.S. Energy Information Administration |
| `COMTRADE_API_KEY` | API key for UN Comtrade data |
| `AISTREAM_API_KEY` | API key for AISStream vessel tracking |
| `SEC_UA` | SEC-required User-Agent string for EDGAR requests |

## Operational Runbook

- **Migrations**: `make migrate` applies the latest database migrations.
- **Health Checks**: `/healthz` for liveness, `/readiness` to verify DB connectivity.
- **Logs**: `docker compose logs -f api`
- **Restart**: `sudo systemctl restart meridian`
- **Metrics**: Visit `/metrics` for Prometheus metrics.

## Data Integration Hub

Run database migrations and start the ingestion stack:

```bash
make migrate
make up
```

Backfill a dataset over a time window:

```bash
python -m ingestion.scheduler.backfill --dataset rates.fred.us10y --start 2023-01-01 --end 2023-12-31
```

### Adding a new dataset

1. Edit `ingestion/registry/datasets.yaml` and add a new entry with the dataset's
   metadata (cadence, adapter path, transform, target table, conflict keys).
2. Implement the adapter class and optional transform function.
3. Run `make migrate` if new tables are required.
4. Start the scheduler with `python -m ingestion.scheduler.run`.

### Schema overview

Key tables powering the risk engine:

- `series`: metadata for each time series (name, unit, geography, etc.).
- `observations`: normalized time series observations keyed by `(series_id, ts)`.
- `factors`: nodes in the cause–effect graph optionally linked to a series.
- `factor_edges`: directed relationships between factors with betas, lags and
  confidence scores.
- `risk_snapshots`: precomputed volatility, shock sizes and cascade impacts per
  factor over time.
- `risk_metrics`: aggregated scores per entity consumed by `/v1/risk`.

### Running the risk engine

The scheduler job `app/scheduler/jobs/risk_metrics.py` recomputes volatilities and
aggregates them into `risk_metrics`. Invoke it manually or wire it into
`apscheduler`.

