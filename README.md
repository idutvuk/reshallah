# RESHALLAh
Утилита для решения примитивных вузовских задач по программированию при помощи LLM с поддержкой MCP и сборкой отчётов по ГОСТу через LaTeX.  Прозиносится как решалА. 

# Установка
1. Клонируйте репозиторий
2. Поставьте докер и запустите его
3. Запустите через bash (git bash если вы на винде)
```bash
docker build -t tex-image . && \
docker run --name tex-container tex-image && \
docker cp tex-container:/template/main.pdf ./ && \
docker rm tex-container
```