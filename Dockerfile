FROM python:3.10-alpine
WORKDIR /registration
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /uaa/requirements.txt
RUN pip install -r requirements.txt
COPY . /registration



