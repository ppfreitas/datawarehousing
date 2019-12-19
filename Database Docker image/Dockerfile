FROM python:3.7

RUN pip install pymongo beautifulsoup4 pandas numpy lxml requests

ADD . .

CMD [ "python", "./mongo.py" ]
