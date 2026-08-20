FROM python:3.11-slim

WORKDIR /app
COPY requirements.lock pyproject.toml README.md ./
COPY veridian ./veridian
COPY titanfuse ./titanfuse
COPY tests ./tests
COPY configs ./configs
COPY examples ./examples

RUN pip install --no-cache-dir -r requirements.lock && pip install --no-cache-dir -e ".[dev]"

EXPOSE 8787 8765
CMD ["veridian", "serve", "--host", "0.0.0.0", "--port", "8787"]
