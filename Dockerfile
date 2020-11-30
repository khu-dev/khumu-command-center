FROM python:3.8
RUN apt-get update -y && apt-get install -y default-libmysqlclient-dev python3-dev
WORKDIR /khumu
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV KHUMU_ENVIRONMENT DEV
# for python print log
ENV PYTHONUNBUFFERED=0
# please mount a config file later (like /khumu/config/dev.yaml)
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]