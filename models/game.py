from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base
from models.move import Move


class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    event = Column(String(50))
    site = Column(String(50))
    date = Column(Date)
    round = Column(String(10))
    white = Column(String(50))
    black = Column(String(50))
    result = Column(String(10))

    moves = relationship("Move", order_by=Move.id, back_populates="game")

    def __repr__(self):
        return "<Game at %s, %s " \
               "(%s vs. %s), " \
               "round %s, " \
               "on %s, " \
               "resulted in %s>" % (
                self.event, self.site,
                self.white, self.black,
                self.round,
                self.date,
                self.result)




