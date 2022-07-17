from sqlalchemy import Column, Integer, String, create_engine

from base import Base


class Season(Base):
    __tablename__ = 'Seasons'

    id = Column(Integer, primary_key=True)
    league_id = Column(Integer)
    year = Column(Integer)
    league_name = Column(String)

    def __repr__(self):
        return (
            f"Season(id={self.id!r}, league_id={self.league_id!r}"
            f", year={self.year!r}, league_name={self.league_name!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
