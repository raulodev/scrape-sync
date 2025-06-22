FROM python:3.12.10-alpine3.21

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN playwright install --with-deps

CMD [ "python", "src/main.py" ]