from sqlalchemy import Column, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship

from base import Base


class Season(Base):
    __tablename__ = 'Seasons'

    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    league_name = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint(
        'league_id', 'year', name='idx_league_year'),)

    setting = relationship("Setting", back_populates="season", uselist=False)
    teams = relationship("Team", back_populates="season")

    def __repr__(self):
        return (
            f"Season(id={self.id!r}, league_id={self.league_id!r}"
            f", year={self.year!r}, league_name={self.league_name!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
