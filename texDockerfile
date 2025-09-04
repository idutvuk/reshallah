FROM texlive/texlive:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      fontconfig \
      apt-utils \
      curl \
      wget \
      unzip && \
      # times new roman
    echo "deb http://deb.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list.d/non-free.list && \
    apt-get update && \
    DEBIAN_FONTEND=noninteractive apt-get install -y --no-install-recommends \
      ttf-mscorefonts-installer && \
    # JetBrains Mono
    mkdir -p /usr/share/fonts/truetype/jetbrains-mono && \
    wget -q https://download.jetbrains.com/fonts/JetBrainsMono-2.304.zip && \
    unzip JetBrainsMono-2.304.zip -d /tmp/jetbrains-mono && \
    cp /tmp/jetbrains-mono/fonts/ttf/*.ttf /usr/share/fonts/truetype/jetbrains-mono && \
    rm -rf /tmp/jetbrains-mono JetBrainsMono-2.304.zip && \
    # font cachupdate
    fc-cache -f -v && \
    rm -rf /var/lib/apt/lists/*

RUN tlmgr install xetex bibtex natbib

# todo govnocode remove
RUN echo '#!/bin/bash\nxelatex -interaction=nonstopmode main.tex\nbibtex main\nxelatex -interaction=nonstopmode main.tex\nxelatex -interaction=nonstopmode main.tex' > /compile.sh \
    && chmod +x /compile.sh

COPY ./template /template
WORKDIR /template

CMD ["/compile.sh"]