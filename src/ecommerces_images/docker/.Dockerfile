FROM python:3.10.11

RUN pip install --upgrade pip

RUN mkdir /usr/src/app
RUN mkdir /usr/src/images

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY ../worker.py .
COPY ../utils.py .

CMD ["python", "worker.py"]