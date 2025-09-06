FROM alpine:latest

# Install required packages
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
    # Add dependencies for building Python packages
    build-base


# Install msttcorefonts and update font cache
RUN update-ms-fonts && \
    fc-cache -f -v

# Set PIP_BREAK_SYSTEM_PACKAGES to bypass the "externally managed" error
ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

# Copy project files
COPY pyproject.toml .

# Install dependencies directly (bypassing the externally managed environment)
RUN pip install -e . --no-cache-dir

RUN apk add --no-cache typst

# Copy application code
COPY server.py .
COPY typst_template/ ./typst_template/

EXPOSE 41434

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "41434", "--reload"]