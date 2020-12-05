FROM python:3.8
USER root

RUN apt-get update
RUN pip install --upgrade pip

WORKDIR /opt/app

COPY docker/deploy/requirements.lock /opt/app
RUN pip install --no-cache-dir -r requirements.lock

COPY ./app /opt/app
 
CMD ["python", "app_deploy.py"]
