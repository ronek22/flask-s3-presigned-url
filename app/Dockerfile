FROM python:3.9.5

RUN pip install pipenv

WORKDIR /flask-deploy

COPY Pipfile* ./
RUN pipenv install --system --skip-lock
RUN pip install gunicorn[gevent]

COPY . .

CMD gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info