FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY services/incident_api/src ./services/incident_api/src

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 5000

CMD ["uv", "run", "flask", "--app", "incident_api.app:create_app", "run", "--host=0.0.0.0"]
