# Etapa 1: build
FROM python:3.11-bullseye AS builder

WORKDIR /app

COPY requirements.txt /app/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary --index-url https://pypi.org/simple --prefix=/install -r requirements.txt

FROM python:3.11-slim AS final

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . /app/
COPY .streamlit /app/.streamlit

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]