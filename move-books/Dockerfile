FROM python:alpine

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY uploader.py /app/uploader.py

RUN mkdir -p /app/books_source
RUN mkdir -p /app/books_destination

CMD ["python", "uploader.py"]