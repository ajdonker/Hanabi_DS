FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server ./server
COPY database ./database
#COPY commands ./server/commands
COPY infrastructure ./infrastructure
EXPOSE 12345
CMD ["python","-m","server.server"]