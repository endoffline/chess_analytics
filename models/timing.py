from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Timing(Base):
    __tablename__ = "timing"

    id = Column(Integer, primary_key=True)
    fullmove_number = Column(Float)
    turn = Column(Float)
    san = Column(Float)
    lan = Column(Float)
    score = Column(Float)
    move_count = Column(Float)
    best_move = Column(Float)
    best_move_score = Column(Float)
    best_move_score_diff = Column(Float)
    best_move_score_diff_category = Column(Float)
    is_check = Column(Float)
    is_capture = Column(Float)
    is_castling = Column(Float)
    possible_moves_count = Column(Float)
    is_capture_count = Column(Float)
    attackers = Column(Float)
    attackers_count = Column(Float)
    threatened_pieces = Column(Float)
    threatened_pieces_count = Column(Float)
    guards = Column(Float)
    guards_count = Column(Float)
    guarded_pieces = Column(Float)
    guarded_pieces_count = Column(Float)
    threatened_guarded_pieces = Column(Float)
    threatened_guarded_pieces_count = Column(Float)
    unopposed_threats = Column(Float)
    unopposed_threats_count = Column(Float)
    pawn_ending = Column(Float)
    rook_ending = Column(Float)

    move_id = Column(Integer, ForeignKey('move.id'))
    move = relationship("Move", back_populates="timing")

    def __repr__(self):
        return "<Move(" \
               "fullmove_number='%s', " \
               "fullmove_number='%s', " \
               "san='%s', lan='%s', " \
               "score='%s')>" % (
                self.id, self.fullmove_number, self.san, self.lan, self.score)