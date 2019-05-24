from sqlalchemy import Column, Float, Integer, String
from models.base import Base


class Timing(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True)
    fullmove_number = Column(Float)
    san = Column(Float)
    lan = Column(Float)
    score = Column(Float)

    def __repr__(self):
        return "<Move(" \
               "fullmove_number='%s', " \
               "fullmove_number='%s', " \
               "san='%s', lan='%s', " \
               "score='%s')>" % (
                self.id, self.fullmove_number, self.san, self.lan, self.score)