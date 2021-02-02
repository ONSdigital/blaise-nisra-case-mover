FROM python:3.6

RUN pip install pipenv==8.2.7

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# FIXME: add pytest to the pipenv file
RUN pip install --no-cache-dir pytest

COPY . .

CMD [ "python", "blaise_nisra_case_mover.py" ]
