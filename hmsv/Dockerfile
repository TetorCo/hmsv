FROM python:3.8
COPY requirements.txt requirements.txt
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN pip install -r requirements.txt
RUN pip install --upgrade pika
RUN pip install python-dotenv
RUN chmod +x /usr/local/bin/wait-for-it
WORKDIR /hmsv
COPY . /hmsv
EXPOSE 80
CMD ["uvicorn", "app.new_app:app", "--host", "0.0.0.0", "--port", "80"]