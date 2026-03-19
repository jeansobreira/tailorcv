FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y texlive-latex-extra texlive-fonts-recommended texlive-lang-portuguese cm-super curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev

COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
