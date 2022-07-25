from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, create_engine
from sqlalchemy.orm import relationship
from base import Base


class Roster(Base):
    __tablename__ = 'Rosters'

    id = Column(Integer, primary_key=True)

    team_id = Column(Integer, ForeignKey('Teams.id'))

    game_id = Column(Integer)
    total_points = Column(Float)
    projected_points = Column(Float)
    scoring_period = Column(Integer)

    team = relationship("Team", back_populates="rosters")

    def __repr__(self):
        return (
            f"Roster(id={self.id!r}"
            f", team_id={self.team_id!r}"
            f", game_id={self.game_id!r}"
            f", total_points={self.total_points!r}"
            f", projected_points={self.projected_points!r}"
            f", scoring_period={self.scoring_period!r})"   
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
