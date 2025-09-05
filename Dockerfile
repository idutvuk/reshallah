FROM python:3.11-slim

# Устанавливаем зависимости и шрифты
RUN echo "deb http://deb.debian.org/debian bookworm main contrib non-free" > /etc/apt/sources.list.d/contrib.list && \
    apt-get update && \
    apt-get install -y ttf-mscorefonts-installer fontconfig && \
    fc-cache -f -v


# Устанавливаем Python-библиотеку typst и FastAPI суппорт
RUN pip install typst \
    fastapi \
    fastapi-mcp \
    uvicorn \
    python-multipart

WORKDIR /app
COPY server.py /app/

EXPOSE 41434
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "41434", "--reload"]
