FROM python:3.10.11

RUN pip install --upgrade pip

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY ../main.py .
COPY ../utils.py .

CMD ["python", "main.py"]