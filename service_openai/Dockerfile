FROM python:3.9

WORKDIR /code/app

EXPOSE 8500

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["python", "main.py"]