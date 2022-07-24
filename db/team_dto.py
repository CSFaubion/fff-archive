from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship
from base import Base


class Team(Base):
    __tablename__ = 'Teams'

    id = Column(Integer, primary_key=True)

    season_id = Column(Integer, ForeignKey('Seasons.id'))
    primary_owner_id = Column(Integer, ForeignKey('Owners.id'))

    espn_team_id = Column(String)
    team_name = Column(String)
    abbrev = Column(String)

    draftpicks = relationship("Draftpick", back_populates="player")
    owners = relationship("Owner", back_populates="teams")
    # TODO: this owners relationship requires more attention. is it many to many?
    # may need to change the ER Diagram and add a members tables as many to many.
    # there can be multiple members per team, but the other relation ship is a
    # primary owner

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
