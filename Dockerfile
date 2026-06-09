FROM cgr.dev/chainguard/python:latest-dev

WORKDIR /app/todo_project

# Instalar dependencias
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copiar codigo fonte da aplicação
COPY . /app

# Environment (override SECRET_KEY and DATABASE_URL at runtime for production)
ENV PYTHONUNBUFFERED=1 \
    SECRET_KEY=change-me \
    DATABASE_URL=sqlite:////tmp/site.db

EXPOSE 5000

# iniciar o aplicativo
CMD ["run.py"]
