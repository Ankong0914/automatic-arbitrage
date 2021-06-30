from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from api_server.database import db

ma = Marshmallow()


class TransactionModel(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    side = db.Column(db.String(255), nullable=False)
    exchange = db.Column(db.String(255), nullable=False)
    balance_jpy = db.Column(db.REAL, nullable=False)
    balance_btc = db.Column(db.REAL, nullable=False)
    bid = db.Column(db.REAL, nullable=False)
    ask = db.Column(db.REAL, nullable=False)
    size = db.Column(db.REAL, nullable=False)
    price = db.Column(db.REAL, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=False)
    contracted_at = db.Column(db.DateTime, nullable=False)
    
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updateTime = db.Column(db.DateTime, nullable=False,
                           default=datetime.now, onupdate=datetime.now)

    def __init__(self, side, exchange, balance_jpy, balance_btc, bid, ask, size, price, ordered_at, contracted_at):
        self.side = side
        self.exchange = exchange
        self.balance_jpy = balance_jpy
        self.balance_btc = balance_btc
        self.bid = bid
        self.ask = ask
        self.size = size
        self.price = price
        self.ordered_at = ordered_at
        self.contracted_at = contracted_at

    def __repr__(self):
        return f'<TransactionModel>'


class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TransactionModel

    created_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
    updated_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
