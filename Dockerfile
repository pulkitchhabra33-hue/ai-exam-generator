FROM python:3.11-slim


WORKDIR /app


# --------------------------------------------------
# SYSTEM DEPENDENCIES
# --------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        default-jre-headless \
        wget \
        unzip \
    && rm -rf /var/lib/apt/lists/*


# --------------------------------------------------
# INSTALL LANGUAGE TOOL
# --------------------------------------------------

ENV LANGUAGETOOL_VERSION=6.8
ENV LANGUAGETOOL_DIR=/opt/languagetool


RUN wget -q \
        https://languagetool.org/download/LanguageTool-${LANGUAGETOOL_VERSION}.zip \
        -O /tmp/languagetool.zip \
    && unzip -q \
        /tmp/languagetool.zip \
        -d /opt \
    && mv \
        /opt/LanguageTool-${LANGUAGETOOL_VERSION} \
        ${LANGUAGETOOL_DIR} \
    && rm \
        /tmp/languagetool.zip


# --------------------------------------------------
# PYTHON DEPENDENCIES
# --------------------------------------------------

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

COPY . .


# Tell language_tool_python where the existing
# LanguageTool installation is located.
ENV LTP_JAR_DIR_PATH=${LANGUAGETOOL_DIR}


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]