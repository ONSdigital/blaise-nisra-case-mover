FROM python:3.6

RUN pip install pipenv==8.2.7

WORKDIR /usr/src/app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

COPY . .

CMD [ "python", "blaise_nisra_transfer.py" ]