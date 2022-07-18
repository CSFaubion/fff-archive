from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref
from base import Base


class Setting(Base):
    __tablename__ = 'Settings'

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('Seasons.id'))

    reg_season_count = Column(Integer)
    veto_votes_required = Column(Integer)
    team_count = Column(Integer)
    playoff_team_count = Column(Integer)
    keeper_count = Column(Integer)
    tie_rule = Column(String)
    playoff_seed_tie_rule = Column(String)

    season = relationship("Season", back_populates="setting")

    
    def __repr__(self):
        return (
            f"Season(id={self.id!r}, league_id={self.league_id!r}"
            f", year={self.year!r}, league_name={self.league_name!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
