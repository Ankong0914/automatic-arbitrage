from flask import Flask, jsonify
from flask_restful import Api

from api_server.database import init_db
from api_server.apis.transaction import TransactionListAPI, TransactionAPI
from api_server.apis.ticker import TickerListAPI, TickerAPI


def create_app():

  app = Flask(__name__)
  app.config.from_object('api_server.config.Config')

  init_db(app)

  api = Api(app)
  api.add_resource(TransactionListAPI, '/transaction')
  api.add_resource(TransactionAPI, '/transaction/<id>')
  api.add_resource(TickerListAPI, '/ticker')
  api.add_resource(TickerAPI, '/ticker/<id>')

  return app


app = create_app()
