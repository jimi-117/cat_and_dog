FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.16 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --frozen

# 環境変数の設定
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    FLASK_RUN_HOST=0.0.0.0

# ポートの公開
EXPOSE 5000 8000

# アプリケーションの実行
CMD ["uv", "run", "flask" "run"]
