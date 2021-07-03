from flask_restful import Resource, reqparse, abort
from flask import jsonify

from api_server.models.ticker import TickerModel, TickerSchema
from api_server.database import db


class TickerListAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('exchange', required=True)
    self.reqparse.add_argument('ask', required=True)
    self.reqparse.add_argument('bid', required=True)
    self.reqparse.add_argument('high', required=True)
    self.reqparse.add_argument('low', required=True)
    self.reqparse.add_argument('volume', required=True)
    self.reqparse.add_argument('timestamp', required=True)
    super(TickerListAPI, self).__init__()


  def get(self):
    results = TickerModel.query.all()
    jsonData = TickerSchema(many=True).dump(results)
    return jsonify({'items': jsonData})


  def post(self):
    args = self.reqparse.parse_args()
    record = TickerModel(args.exchange, args.ask, args.bid, args.high, args.low, args.volume, args.timestamp) # TODO
    db.session.add(record)
    db.session.commit()
    res = TickerSchema().dump(record)
    return res, 201


class TickerAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('exchange', required=True)
    self.reqparse.add_argument('ask', required=True)
    self.reqparse.add_argument('bid', required=True)
    self.reqparse.add_argument('high', required=True)
    self.reqparse.add_argument('low', required=True)
    self.reqparse.add_argument('volume', required=True)
    self.reqparse.add_argument('timestamp', required=True)
    super(TickerAPI, self).__init__()


  def get(self, id):
    record = db.session.query(TickerModel).filter_by(id=id).first()
    if record == None:
      abort(404)

    res = TickerSchema().dump(record)
    return res


  def put(self, id):
    record = db.session.query(TickerModel).filter_by(id=id).first()
    if record == None:
      abort(404)
    args = self.reqparse.parse_args()
    for name, value in args.items():
      if value is not None:
        setattr(record, name, value)
    db.session.add(record)
    db.session.commit()
    return None, 204


  def delete(self, id):
    record = db.session.query(TickerModel).filter_by(id=id).first()
    if record is not None:
      db.session.delete(record)
      db.session.commit()
    return None, 204


class TickerByExchange(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('begin', type=str)  # TODO: apply above classes
    self.reqparse.add_argument('end', type=str)
    super(TickerByExchange, self).__init__()
  
  def get(self, exchange):
    results = TickerModel.query.filter_by(exchange=exchange)
    if results == None:
      abort(404)
    jsonData = TickerSchema(many=True).dump(results)
    return jsonify({'items': jsonData})
