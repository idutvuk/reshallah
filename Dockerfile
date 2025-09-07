FROM alpine:latest

RUN apk add --no-cache \
    python3 \
    py3-pip \
    msttcorefonts-installer \
    fontconfig \
    zip \
    unzip \
    gcc \
    python3-dev \
    musl-dev \
    typst \
    build-base


# add times new roman
RUN update-ms-fonts && \
    fc-cache -f -v

ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

COPY pyproject.toml .

RUN pip install -e . --no-cache-dir

COPY server.py .
COPY typst_template/ ./typst_template/

EXPOSE 41434

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "41434", "--reload"]