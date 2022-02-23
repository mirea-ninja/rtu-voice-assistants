FROM python:latest
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN python -m pip install -r ./requirements.txt
COPY . /app
WORKDIR /
EXPOSE 8000
ENTRYPOINT uvicorn --host 0.0.0.0 --port 8000 app.app:app