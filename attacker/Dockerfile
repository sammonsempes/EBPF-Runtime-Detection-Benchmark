FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/attacker
COPY server.py /opt/attacker/server.py

EXPOSE 3333 4444 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
    CMD python3 -c "import socket; socket.create_connection(('127.0.0.1', 8080), timeout=2).close()"

CMD ["python3", "/opt/attacker/server.py"]
