FROM python:3.10-slim-buster 

WORKDIR /app

RUN apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get install -y gcc


RUN pip install --upgrade pip 

COPY ./pyproject.toml .

RUN pip install .

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
