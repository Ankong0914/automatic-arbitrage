FROM python:3.8-slim
COPY requirements.txt /transaction_system/src/
RUN pip install -r /transaction_system/src/requirements.txt
COPY . /transaction_system/src/
WORKDIR /transaction_system/src
CMD ["python", "confirm.py"]