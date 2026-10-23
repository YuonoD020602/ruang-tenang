# Satu image untuk backend dan frontend; perintah dijalankan berbeda di docker-compose.yml
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt requirements-train.txt ./
ARG INSTALL_TRAIN=false
RUN pip install -r requirements.txt && \
    if [ "$INSTALL_TRAIN" = "true" ]; then pip install -r requirements-train.txt; fi

COPY src ./src
COPY knowledge ./knowledge
COPY models ./models
COPY data ./data
COPY .streamlit ./.streamlit

# pengguna non-root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000 8501
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
