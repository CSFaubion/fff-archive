from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship
from base import Base


class Owner(Base):
    __tablename__ = 'Owners'

    id = Column(Integer, primary_key=True)

    first_name = Column(String)
    last_name = Column(String)
    espn_owner_id = Column(String)
    display_name = Column(String)


    teams = relationship("Team", back_populates="draftpicks")

    def __repr__(self):
        return (
            f"Player(id={self.id!r}"
            f", espn_player_name={self.espn_player_name!r}"
            f", position={self.position!r}"
            f", espn_id={self.espn_id!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
