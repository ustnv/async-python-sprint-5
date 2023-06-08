FROM python:3.10.8

WORKDIR app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN apt -y update \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src .


# run alembic migrations
RUN alembic upgrade head

# run the application uvicorn
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9010" ]
#CMD [ "python", "main.py" ]

