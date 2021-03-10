FROM python:3
WORKDIR /usr/src/app
COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
CMD ["python3", "app.py"]
