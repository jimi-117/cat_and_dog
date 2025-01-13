FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /opt/app

COPY . .
RUN pip install .
EXPOSE 5000
CMD ["python3","app.py"]