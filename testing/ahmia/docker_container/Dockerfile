FROM python:3.10

ADD main.py .

ADD requirements.txt .

ENV keyword drugname


RUN pip install -r requirements.txt

CMD python -u ./main.py -k "$keyword"
