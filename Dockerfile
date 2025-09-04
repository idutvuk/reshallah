FROM ghcr.io/typst/typst:v0.13.1


# Install required packages and Times New Roman font
RUN apk update && \
    apk add --no-cache \
    msttcorefonts-installer \
    fontconfig && \
    update-ms-fonts && \
    fc-cache -f

#
## Создаем директорию для пользовательских шрифтов внутри контейнера
#RUN mkdir -p /usr/share/fonts/custom
#
#COPY fonts/ /usr/share/fonts/custom/
#
#RUN if command -v fc-cache >/dev/null 2>&1; then fc-cache -f -v; fi

COPY typst_template/ typst_template/

WORKDIR typst_template

CMD ["compile", "main.typ"]