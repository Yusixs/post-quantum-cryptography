FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment first
COPY venv /app/venv

# Copy application files
COPY app /app/app
COPY requirements.txt /app/

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 