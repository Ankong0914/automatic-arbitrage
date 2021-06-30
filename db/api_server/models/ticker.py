from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from api_server.database import db

ma = Marshmallow()


class TickerModel(db.Model):
    __tablename__ = 'ticker'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    exchange = db.Column(db.String(255), nullable=False)
    ask = db.Column(db.REAL, nullable=False)
    bid = db.Column(db.REAL, nullable=False)
    high = db.Column(db.REAL, nullable=False)
    low = db.Column(db.REAL, nullable=False)
    volume = db.Column(db.REAL, nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)

    def __init__(self, exchange, ask, bid, high, low, volume, timestamp):
        self.exchange = exchange
        self.ask = ask
        self.bid = bid
        self.high = high
        self.low = low
        self.volume = volume
        self.timestamp = timestamp

    def __repr__(self):
        return f'<TickerModel>'


class TickerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TickerModel

    created_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
    updated_at = fields.DateTime('%Y-%m-%dT%H:%M:%S')
