FROM python:alpine
WORKDIR /app
RUN mkdir -p /books_source
RUN mkdir -p /books_destination
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY uploader.py /app/uploader.py
CMD ["python", "uploader.py"]

