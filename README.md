# Meridian Backend

This project provides a minimal foundation for an analytics platform using FastAPI.

## Development

```bash
poetry install
cp .env.example .env
make fmt
make lint
make test
```

Run the service:

```bash
uvicorn app.main:app --reload
```

Docker compose for local dependencies:

```bash
make up
```
