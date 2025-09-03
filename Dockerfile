FROM texlive/texlive:latest

# Настроим репозитории и установим шрифты
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      fontconfig \
      apt-utils \
      curl && \
    echo "deb http://deb.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list.d/non-free.list && \
    apt-get update && \
    DEBIAN_FONTEND=noninteractive apt-get install -y --no-install-recommends \
      ttf-mscorefonts-installer && \
    fc-cache -f -v && \
    rm -rf /var/lib/apt/lists/*

# Установим необходимые пакеты для XeLaTeX (если нужны)
RUN tlmgr install xetex

# Копируем шаблон
COPY ./template /template
WORKDIR /template

# Компиляция XeLaTeX
CMD xelatex -interaction=nonstopmode main.tex