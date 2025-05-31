FROM python:3.13-slim
RUN pip install fastapi uvicorn

COPY validator.py .

EXPOSE 80
ENTRYPOINT uvicorn validator:app --host 0.0.0.0 --port 80