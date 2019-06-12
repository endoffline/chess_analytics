from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from models.score import Score
from models.timing import Timing


class Move(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True)
    fullmove_number = Column(Integer)
    ply_number = Column(Integer)
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
    captures = Column(String(50))
    is_capture_count = Column(Integer)
    attackers_white = Column(String(50))
    attackers_count_white = Column(Integer)
    threatened_pieces_white = Column(String(50))
    threatened_pieces_count_white = Column(Integer)
    guards_white = Column(String(50))
    guards_count_white = Column(Integer)
    guarded_pieces_white = Column(String(50))
    guarded_pieces_count_white = Column(Integer)
    threatened_guarded_pieces_white = Column(String(50))
    threatened_guarded_pieces_count_white = Column(Integer)
    unopposed_threats_white = Column(String(50))
    unopposed_threats_count_white = Column(Integer)
    attackers_black = Column(String(50))
    attackers_count_black = Column(Integer)
    threatened_pieces_black = Column(String(50))
    threatened_pieces_count_black = Column(Integer)
    guards_black = Column(String(50))
    guards_count_black = Column(Integer)
    guarded_pieces_black = Column(String(50))
    guarded_pieces_count_black = Column(Integer)
    threatened_guarded_pieces_black = Column(String(50))
    threatened_guarded_pieces_count_black = Column(Integer)
    unopposed_threats_black = Column(String(50))
    unopposed_threats_count_black = Column(Integer)
    score_shift = Column(Integer)
    score_shift_category = Column(Float)
    threatened_pieces_centipawn_white = Column(Integer)
    guarded_pieces_centipawn_white = Column(Integer)
    threatened_guarded_pieces_centipawn_white = Column(Integer)
    unopposed_threats_centipawn_white = Column(Integer)
    threatened_pieces_centipawn_black = Column(Integer)
    guarded_pieces_centipawn_black = Column(Integer)
    threatened_guarded_pieces_centipawn_black = Column(Integer)
    unopposed_threats_centipawn_black = Column(Integer)
    attackers_count_all = Column(Integer)
    threatened_pieces_count_all = Column(Integer)
    guards_count_all = Column(Integer)
    guarded_pieces_count_all = Column(Integer)
    threatened_guarded_pieces_count_all = Column(Integer)
    unopposed_threats_count_all = Column(Integer)
    threatened_pieces_centipawn_all = Column(Integer)
    guarded_pieces_centipawn_all = Column(Integer)
    threatened_guarded_pieces_centipawn_all = Column(Integer)
    unopposed_threats_centipawn_all = Column(Integer)
    pawn_ending = Column(Boolean)
    rook_ending = Column(Boolean)

    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship("Game", back_populates="moves")

    scores = relationship("Score", uselist=False, back_populates="move")
    timing = relationship("Timing", uselist=False, back_populates="move")

    def __repr__(self):
        return "<Move(" \
               "fullmove_number='%s', " \
               "san='%s', lan='%s', " \
               "score='%s')>" % (
                self.fullmove_number, self.san, self.lan, self.score)

    #def score(self):
    # return self.score

