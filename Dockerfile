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
# PYTHON DEPENDENCIES
# --------------------------------------------------

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


# --------------------------------------------------
# LANGUAGE TOOL
# --------------------------------------------------

ENV LTP_PATH=/opt/languagetool


RUN python -c "import language_tool_python; language_tool_python.LanguageTool('en-US').close()"


ENV LTP_JAR_DIR_PATH=/opt/languagetool


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

COPY . .


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]