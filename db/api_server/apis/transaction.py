from flask_restful import Resource, reqparse, abort
from flask import jsonify

from api_server.models.transaction import TransactionModel, TransactionSchema
from api_server.database import db


class TransactionListAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('side', required=True)
    self.reqparse.add_argument('exchange', required=True)
    self.reqparse.add_argument('balance_jpy', required=True)
    self.reqparse.add_argument('balance_btc', required=True)
    self.reqparse.add_argument('bid', required=True)
    self.reqparse.add_argument('ask', required=True)
    self.reqparse.add_argument('size', required=True)
    self.reqparse.add_argument('price', required=True)
    self.reqparse.add_argument('ordered_at', required=True)
    self.reqparse.add_argument('contracted_at', required=True)
    super(TransactionListAPI, self).__init__()


  def get(self):
    results = TransactionModel.query.all()
    jsonData = TransactionSchema(many=True).dump(results)
    return jsonify({'items': jsonData})


  def post(self):
    args = self.reqparse.parse_args()
    record = TransactionModel(args.side, args.exchange, args.balance_jpy, args.balance_btc, args.bid, args.ask, args.size, args.price, args.ordered_at, args.contracted_at) # TODO
    db.session.add(record)
    db.session.commit()
    res = TransactionSchema().dump(record)
    return res, 201


class TransactionAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('side', required=True)
    self.reqparse.add_argument('exchange', required=True)
    self.reqparse.add_argument('balance_jpy', required=True)
    self.reqparse.add_argument('balance_btc', required=True)
    self.reqparse.add_argument('bid', required=True)
    self.reqparse.add_argument('ask', required=True)
    self.reqparse.add_argument('size', required=True)
    self.reqparse.add_argument('price', required=True)
    self.reqparse.add_argument('ordered_at', required=True)
    self.reqparse.add_argument('contracted_at', required=True)
    super(TransactionAPI, self).__init__()


  def get(self, id):
    record = db.session.query(TransactionModel).filter_by(id=id).first()
    if record == None:
      abort(404)

    res = TransactionSchema().dump(record)
    return res


  def put(self, id):
    record = db.session.query(TransactionModel).filter_by(id=id).first()
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
    record = db.session.query(TransactionModel).filter_by(id=id).first()
    if record is not None:
      db.session.delete(record)
      db.session.commit()
    return None, 204
