FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock README.md /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main
COPY . /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
