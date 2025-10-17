FROM python:3.12-slim
RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY . .
RUN pip install fastapi[all] uvicorn google-generativeai pygithub python-dotenv aiohttp requests
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]