from sqlalchemy import (Boolean, Column, ForeignKey, Integer, UniqueConstraint,
                        create_engine)
from sqlalchemy.orm import relationship

from base import Base


class Draftpick(Base):
    __tablename__ = 'Draftpicks'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Teams.id'))
    player_id = Column(Integer, ForeignKey('Players.id'))
    round_num = Column(Integer)
    round_pick = Column(Integer)
    pick_number = Column(Integer)
    bid_amount = Column(Integer)
    keeper_status = Column(Boolean)

    __table_args__ = (UniqueConstraint(
        'team_id', 'pick_number', name='idx_team_id_pick_number'),)

    player = relationship("Player", back_populates="draftpicks")
    team = relationship("Team", back_populates="draftpicks")

    def __repr__(self):
        return (
            f"Draftpick(id={self.id!r}"
            f", team_id={self.team_id!r}"
            f", player_id={self.player_id!r}"
            f", round_num={self.round_num!r}"
            f", round_pick={self.round_pick!r}"
            f", pick_number={self.pick_number!r}"
            f", bid_amount={self.bid_amount!r}"
            f", keeper_status={self.keeper_status!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
