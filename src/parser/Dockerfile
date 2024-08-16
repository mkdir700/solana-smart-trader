FROM python:3.10-slim

WORKDIR /app

# 安装 PDM
RUN pip install --no-cache-dir pdm

COPY pyproject.toml ./
COPY pdm.lock ./

RUN pdm install --prod

COPY . .

CMD ["pdm", "run", "python", "app.py"]
