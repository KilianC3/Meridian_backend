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

