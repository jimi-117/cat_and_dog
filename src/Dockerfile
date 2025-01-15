FROM python:3.11-slim

WORKDIR /app

# 依存関係のファイルをコピー
COPY pyproject.toml setup.py ./

# srcディレクトリの内容をコピー
COPY src/ ./src/

# モデルファイルを確実にコピー
COPY src/models/model.keras ./src/models/

# パッケージをインストール
RUN pip install -e .

EXPOSE 5000
CMD ["python3", "src/app.py"]