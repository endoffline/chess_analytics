from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Move(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True)
    fullmove_number = Column(Integer)
    turn = Column(Boolean)
    san = Column(String(10))
    lan = Column(String(10))
    score = Column(Integer)
    move_count = Column(Integer)
    best_move = Column(String(10))
    best_move_score = Column(Integer)
    best_move_score_diff = Column(Integer)
    best_move_score_diff_category = Column(Integer)
    is_check = Column(Boolean)
    is_capture = Column(Boolean)
    is_castling = Column(Boolean)
    possible_moves_count = Column(Integer)
    is_capture_count = Column(Integer)
    attackers = Column(String(50))
    attackers_count = Column(Integer)
    threatened_pieces = Column(String(50))
    threatened_pieces_count = Column(Integer)
    guards = Column(String(50))
    guards_count = Column(Integer)
    guarded_pieces = Column(String(50))
    guarded_pieces_count = Column(Integer)
    threatened_guarded_pieces = Column(String(50))
    threatened_guarded_pieces_count = Column(Integer)
    unopposed_threats = Column(String(50))
    unopposed_threats_count = Column(Integer)
    pawn_ending = Column(Boolean)
    rook_ending = Column(Boolean)

    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship("Game", back_populates="moves")

    def __repr__(self):
        return "<Move(" \
               "fullmove_number='%s', " \
               "fullmove_number='%s', " \
               "san='%s', lan='%s', " \
               "score='%s')>" % (
                self.id, self.fullmove_number, self.san, self.lan, self.score)

