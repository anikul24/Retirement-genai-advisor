# Use a lightweight Python base image
FROM python:3.10-slim

# 1. Install System Dependencies (The Resume "Hard Skill")
# We explicitly install Tesseract and Poppler for Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Application Directory
WORKDIR /app

# 3. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Code
COPY . .

# 5. Set Tesseract Path for Linux
# (Note: In Linux, tesseract is usually at /usr/bin/tesseract)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# 6. Expose Port and Run
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]