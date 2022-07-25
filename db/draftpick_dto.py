from sqlalchemy import Boolean, Column, ForeignKey, Integer, create_engine
from sqlalchemy.orm import relationship

from base import Base


class Draftpick(Base):
    __tablename__ = 'Draftpicks'

    id = Column(Integer, primary_key=True)

    team_id = Column(Integer, ForeignKey('Teams.id'))
    player_id = Column(Integer, ForeignKey('Players.id'))

    round_number = Column(Integer)
    round_pick = Column(Integer)
    pick_number = Column(Integer)
    bid_amount = Column(Integer)
    keeper_status = Column(Boolean)

    player = relationship("Player", back_populates="draftpicks")

    def __repr__(self):
        return (
            f"Draftpick(id={self.id!r}"
            f", team_id={self.team_id!r}"
            f", player_id={self.player_id!r}"
            f", round_number={self.round_number!r}"
            f", round_pick={self.round_pick!r}"
            f", pick_number={self.pick_number!r}"
            f", bid_amount={self.bid_amount!r}"
            f", keeper_status={self.keeper_status!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
