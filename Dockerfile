FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY game_logic ./game_logic
COPY server ./server
EXPOSE 12345
CMD ["python","-m","server.server"]