from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, String,
                        UniqueConstraint, create_engine)
from sqlalchemy.orm import relationship

from base import Base


class Stat(Base):
    __tablename__ = 'Stats'

    id = Column(Integer, primary_key=True)

    player_id = Column(Integer, ForeignKey('Players.id'))
    roster_id = Column(Integer, ForeignKey('Rosters.id'))

    total_points = Column(Float)
    projected_points = Column(Float)
    starting = Column(Boolean)
    position = Column(String)
    pro_team = Column(String)
    scoring_period = Column(Integer)

    __table_args__ = (UniqueConstraint(
        'player_id', 'roster_id', name='idx_player_roster'),)

    player = relationship("Player", back_populates="stats")
    roster = relationship("Roster", back_populates="stats")

    def __repr__(self):
        return (
            f"Stat(id={self.id!r},"
            f" player_id = {self.player_id!r},"
            f" roster_id = {self.roster_id!r},"
            f" total_points = {self.total_points!r},"
            f" projected_points = {self.projected_points!r},"
            f" starting = {self.starting!r},"
            f" position = {self.position!r},"
            f" pro_team = {self.pro_team!r},"
            f" scoring_period = {self.scoring_period!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
