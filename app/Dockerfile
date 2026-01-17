FROM python:3.12.12-slim AS build
WORKDIR /app/src
COPY info/requirements.txt /app/info/requirements.txt
RUN pip3 install --no-cache-dir -r /app/info/requirements.txt
COPY src/ /app/src/
RUN adduser --disabled-password --gecos '' user && \
    chown -R user:user /app/src/ && \
    chmod -R 755 /app/src/
USER user
EXPOSE 5000
CMD ["python3", "main.py"]