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
| `POSTGRES_DSN` | PostgreSQL connection string |
| `MONGO_DSN` | MongoDB connection string |
| `REDIS_DSN` | Redis connection string |
| `SECRET_KEY` | Secret key for signing tokens |
| `SENTRY_DSN` | Optional Sentry DSN for error tracking |
| `PING_TIMEOUT` | Timeout in seconds for dependency health checks |
| `READINESS_CACHE_TTL` | TTL in seconds for cached readiness results |
| `CORS_ORIGINS` | Comma separated list of allowed CORS origins |

## Operational Runbook

- **Migrations**: `make migrate` applies the latest database migrations.
- **Health Checks**: `/healthz` for liveness, `/readiness` to verify DB connectivity.
- **Logs**: `docker compose logs -f api`
- **Restart**: `sudo systemctl restart meridian`
- **Metrics**: Visit `/metrics` for Prometheus metrics.

