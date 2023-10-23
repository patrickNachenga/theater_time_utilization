#FROM python:3.10-alpine
#WORKDIR /registration
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONBUFFERED 1
# install system dependencies
#RUN apt-get update \
#  && apt-get -y install netcat gcc postgresql \
#  && apt-get clean
# install python dependencies
#RUN pip install --no-cache-dir --upgrade pip
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8804", "--reload"]



FROM python:3.10-buster
RUN apt-get update && apt-get --yes install build-essential python3-dev libmemcached-dev libldap2-dev libsasl2-dev libzbar-dev ldap-utils tox lcov valgrind && \
apt-get clean
WORKDIR /registration
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
# install system dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install redis
RUN pip install uvicorn[standard]
#CMD rq worker --with-scheduler
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8804", "--reload"]



