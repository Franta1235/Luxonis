FROM python:latest
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ADD requirements.txt requirements.txt
RUN apt-get update && apt-get install --assume-yes chromium
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]