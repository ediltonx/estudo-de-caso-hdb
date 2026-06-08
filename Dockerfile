FROM cgr.dev/chainguard/python:latest-dev

WORKDIR /app/todo_project

# Install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Environment (override SECRET_KEY and DATABASE_URL at runtime for production)
ENV PYTHONUNBUFFERED=1 \
    SECRET_KEY=change-me \
    DATABASE_URL=sqlite:////tmp/site.db

EXPOSE 5000

# Start the app through the existing project entrypoint
CMD ["run.py"]
