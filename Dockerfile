FROM python:3.7-alpine
RUN mkdir /code && apk add cmake build-base jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib PYTHONBUFFERED=1
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
CMD ["python", "main.py"]
