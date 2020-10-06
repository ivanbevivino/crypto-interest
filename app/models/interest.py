from app.models.mixins import BaseModel
from . import db
from enum import Enum


class Platform(Enum):
    AAVE = "aave"
    COMPOUND = "compound"


class Interest(BaseModel):
    __versioned__ = {"strategy": "subquery"}
    __tablename__ = "interest"

    id = db.Column(db.BigInteger, primary_key=True)
    plataform = db.Column(db.Enum(Platform))
    interest = db.Column(db.Float(2))
    date = db.Column(db.DateTime)


    def serialize(self):
        d = dict()
        d["id"] = self.id
        d["plataform"] = self.plataform.value
        d["interest"] = self.interest
        d["date"] = self.date
        return d

