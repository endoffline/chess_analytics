from sqlalchemy import Column, Float, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class TimingScore(Base):
    __tablename__ = "timing_score"

    id = Column(Integer, primary_key=True)
    score_a0010 = Column(Float)
    score_a0020 = Column(Float)
    score_a0050 = Column(Float)
    score_a0100 = Column(Float)
    score_a0200 = Column(Float)
    score_a0500 = Column(Float)
    score_a1000 = Column(Float)
    score_a2000 = Column(Float)
    score_a5000 = Column(Float)
    best_move_a0010 = Column(Float)
    best_move_a0020 = Column(Float)
    best_move_a0050 = Column(Float)
    best_move_a0100 = Column(Float)
    best_move_a0200 = Column(Float)
    best_move_a0500 = Column(Float)
    best_move_a1000 = Column(Float)
    best_move_a2000 = Column(Float)
    best_move_a5000 = Column(Float)
    best_move_score_a0010 = Column(Float)
    best_move_score_a0020 = Column(Float)
    best_move_score_a0050 = Column(Float)
    best_move_score_a0100 = Column(Float)
    best_move_score_a0200 = Column(Float)
    best_move_score_a0500 = Column(Float)
    best_move_score_a1000 = Column(Float)
    best_move_score_a2000 = Column(Float)
    best_move_score_a5000 = Column(Float)
    best_move_score_diff_a0010 = Column(Float)
    best_move_score_diff_a0020 = Column(Float)
    best_move_score_diff_a0050 = Column(Float)
    best_move_score_diff_a0100 = Column(Float)
    best_move_score_diff_a0200 = Column(Float)
    best_move_score_diff_a0500 = Column(Float)
    best_move_score_diff_a1000 = Column(Float)
    best_move_score_diff_a2000 = Column(Float)
    best_move_score_diff_a5000 = Column(Float)
    best_move_score_diff_category_a0010 = Column(Float)
    best_move_score_diff_category_a0020 = Column(Float)
    best_move_score_diff_category_a0050 = Column(Float)
    best_move_score_diff_category_a0100 = Column(Float)
    best_move_score_diff_category_a0200 = Column(Float)
    best_move_score_diff_category_a0500 = Column(Float)
    best_move_score_diff_category_a1000 = Column(Float)
    best_move_score_diff_category_a2000 = Column(Float)
    best_move_score_diff_category_a5000 = Column(Float)

    score_b0010 = Column(Float)
    score_b0020 = Column(Float)
    score_b0050 = Column(Float)
    score_b0100 = Column(Float)
    score_b0200 = Column(Float)
    score_b0500 = Column(Float)
    score_b1000 = Column(Float)
    score_b2000 = Column(Float)
    score_b5000 = Column(Float)
    best_move_b0010 = Column(Float)
    best_move_b0020 = Column(Float)
    best_move_b0050 = Column(Float)
    best_move_b0100 = Column(Float)
    best_move_b0200 = Column(Float)
    best_move_b0500 = Column(Float)
    best_move_b1000 = Column(Float)
    best_move_b2000 = Column(Float)
    best_move_b5000 = Column(Float)
    best_move_score_b0010 = Column(Float)
    best_move_score_b0020 = Column(Float)
    best_move_score_b0050 = Column(Float)
    best_move_score_b0100 = Column(Float)
    best_move_score_b0200 = Column(Float)
    best_move_score_b0500 = Column(Float)
    best_move_score_b1000 = Column(Float)
    best_move_score_b2000 = Column(Float)
    best_move_score_b5000 = Column(Float)
    best_move_score_diff_b0010 = Column(Float)
    best_move_score_diff_b0020 = Column(Float)
    best_move_score_diff_b0050 = Column(Float)
    best_move_score_diff_b0100 = Column(Float)
    best_move_score_diff_b0200 = Column(Float)
    best_move_score_diff_b0500 = Column(Float)
    best_move_score_diff_b1000 = Column(Float)
    best_move_score_diff_b2000 = Column(Float)
    best_move_score_diff_b5000 = Column(Float)
    best_move_score_diff_category_b0010 = Column(Float)
    best_move_score_diff_category_b0020 = Column(Float)
    best_move_score_diff_category_b0050 = Column(Float)
    best_move_score_diff_category_b0100 = Column(Float)
    best_move_score_diff_category_b0200 = Column(Float)
    best_move_score_diff_category_b0500 = Column(Float)
    best_move_score_diff_category_b1000 = Column(Float)
    best_move_score_diff_category_b2000 = Column(Float)
    best_move_score_diff_category_b5000 = Column(Float)

    score_id = Column(Integer, ForeignKey('score.id'))
    score = relationship("Score", back_populates="timing_score")

    def __repr__(self):
        return "<Score(" \
               "score_a='%d', " \
               "score_b='%d', " \
               ")>" % (
                self.score_a0100, self.score_b0100)
