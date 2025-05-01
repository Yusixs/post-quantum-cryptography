FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment
COPY venv /app/venv

# Copy application files
COPY app /app/app
COPY requirements.txt /app/

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/venv/lib/python3.11/site-packages"
ENV VIRTUAL_ENV="/app/venv"

# Make sure we're using the virtual environment's Python
RUN ln -s /app/venv/bin/python /usr/local/bin/python

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 