FROM python:3.12-slim

WORKDIR /app

# Install dependencies required by your project (like PyPDF2, etc)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application
COPY . .

# Expose backend port
EXPOSE 3008

# Setup volume for persistent data
VOLUME ["/app/data", "/app/temp"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3008"]
