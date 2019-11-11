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
    whiteelo = Column(Integer)
    blackelo = Column(Integer)
    result = Column(String(10))
    length = Column(Integer)
    moves = relationship("Move", order_by=Move.id, back_populates="game")

    def __repr__(self):
        return "<Game at %s, %s " \
               "[%s(%s) vs. %s(%s)], " \
               "round %s, " \
               "on %s, " \
               "resulted in %s>" % (
                self.event, self.site,
                self.white, self.whiteelo, self.black, self.blackelo,
                self.round,
                self.date,
                self.result)




