FROM python:3.14.0a4-alpine3.21

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN playwright install
RUN pip install fastapi[standard]
CMD ["fastapi", "run"]
