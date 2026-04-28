FROM python:3.12-slim

RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install .

CMD ["python", "-m", "sila2_driver.thermoscientific.teleshake1536"]