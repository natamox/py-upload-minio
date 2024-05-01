FROM python:3.8-slim

RUN if [ "$(uname -m)" = "aarch64" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends build-essential; \
    else \
        echo "Not installing build-essential for non-arm64 architectures"; \
    fi

WORKDIR /app

COPY app.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
