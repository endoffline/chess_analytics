from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Timing(Base):
    __tablename__ = "timing"

    id = Column(Integer, primary_key=True)
    fullmove_number = Column(Float)
    ply_number = Column(Integer)
    turn = Column(Float)
    san = Column(Float)
    lan = Column(Float)
    score = Column(Float)
    score_change = Column(Float)
    score_change_category = Column(Float)
    move_count = Column(Float)
    best_move = Column(Float)
    best_move_score = Column(Float)
    best_move_score_diff = Column(Float)
    best_move_score_diff_category = Column(Float)
    is_check = Column(Float)
    is_capture = Column(Float)
    is_castling = Column(Float)
    possible_moves_count = Column(Float)
    possible_moves_quality = Column(Float)
    captures = Column(Float)
    is_capture_count = Column(Float)
    is_capture_weighted = Column(Float)

    attackers_white = Column(Float)
    attackers_count_white = Column(Float)
    attacked_pieces_white = Column(Float)
    attacked_pieces_count_white = Column(Float)
    guards_white = Column(Float)
    guards_count_white = Column(Float)
    guarded_pieces_white = Column(Float)
    guarded_pieces_count_white = Column(Float)
    attacked_guarded_pieces_white = Column(Float)
    attacked_guarded_pieces_count_white = Column(Float)
    unopposed_threats_white = Column(Float)
    unopposed_threats_count_white = Column(Float)
    threats_count_white = Column(Float)
    forking_pieces_white = Column(Float)
    fork_count_white = Column(Float)
    pin_count_white = Column(Float)
    skewer_count_white = Column(Float)

    attackers_black = Column(Float)
    attackers_count_black = Column(Float)
    attacked_pieces_black = Column(Float)
    attacked_pieces_count_black = Column(Float)
    guards_black = Column(Float)
    guards_count_black = Column(Float)
    guarded_pieces_black = Column(Float)
    guarded_pieces_count_black = Column(Float)
    attacked_guarded_pieces_black = Column(Float)
    attacked_guarded_pieces_count_black = Column(Float)
    unopposed_threats_black = Column(Float)
    unopposed_threats_count_black = Column(Float)
    threats_count_black = Column(Float)
    forking_pieces_black = Column(Float)
    fork_count_black = Column(Float)
    pin_count_black = Column(Float)
    skewer_count_black = Column(Float)

    attacked_pieces_centipawn_white = Column(Float)
    threats_centipawn_white = Column(Float)
    threats_centipawn_black = Column(Float)
    attack_defense_relation1 = Column(Float)
    attack_defense_relation2 = Column(Float)
    material = Column(Float)
    pawn_ending = Column(Float)
    rook_ending = Column(Float)
    time = Column(Float)

    move_id = Column(Integer, ForeignKey('move.id'))
    move = relationship("Move", back_populates="timing")

    def __repr__(self):
        return "<Move(" \
               "fullmove_number='%s', " \
               "fullmove_number='%s', " \
               "san='%s', lan='%s', " \
               "score='%s')>" % (
                self.id, self.fullmove_number, self.san, self.lan, self.score)