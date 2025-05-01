FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y \
    git build-essential cmake libssl-dev unzip && \
    apt-get clean

# Create virtual environment
RUN uv venv

# Install Python dependencies first
COPY requirements.txt .
RUN . .venv/bin/activate && \
    uv pip install --upgrade pip && \
    uv pip install -r requirements.txt

# Clone pqcrypto + submodules and install
RUN . .venv/bin/activate && \
    git clone https://github.com/backbone-hq/pqcrypto.git && \
    cd pqcrypto && \
    git submodule update --init --recursive && \
    # Create proper pyproject.toml
    echo '[project]' > pyproject.toml && \
    echo 'name = "pqcrypto"' >> pyproject.toml && \
    echo 'version = "0.3.1"' >> pyproject.toml && \
    echo 'description = "Post-quantum cryptography for Python."' >> pyproject.toml && \
    echo 'authors = [{ name = "Backbone Authors", email = "root@backbone.dev" }]' >> pyproject.toml && \
    echo 'license = { text = "Apache-2.0" }' >> pyproject.toml && \
    echo 'readme = "README.md"' >> pyproject.toml && \
    echo 'keywords = ["post-quantum", "cryptography", "security", "pqclean"]' >> pyproject.toml && \
    echo 'requires-python = ">=3.9"' >> pyproject.toml && \
    echo '[build-system]' >> pyproject.toml && \
    echo 'requires = ["hatchling", "cffi", "jinja2", "setuptools"]' >> pyproject.toml && \
    echo 'build-backend = "hatchling.build"' >> pyproject.toml && \
    echo '[tool.setuptools]' >> pyproject.toml && \
    echo 'py-modules = ["pqcrypto"]' >> pyproject.toml && \
    # Use uv to compile
    uv pip install hatchling cffi jinja2 setuptools && \
    python compile.py && \
    # Copy from inner pqcrypto/ subfolder to site-packages
    mkdir -p /usr/local/lib/python3.11/site-packages/pqcrypto/ && \
    cp -r pqcrypto/kem pqcrypto/_kem pqcrypto/sign pqcrypto/_sign pqcrypto/__init__.py /usr/local/lib/python3.11/site-packages/pqcrypto/

# Copy app code
COPY . .

# Run your FastAPI app
CMD ["/bin/bash", "-c", ". .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
