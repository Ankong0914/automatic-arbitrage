FROM python:3.8-slim
COPY . /transaction_system/src
WORKDIR /transaction_system/src
RUN pip install -r requirements.txt
CMD ["python", "arbitrage.py"]