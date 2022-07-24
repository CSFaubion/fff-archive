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
    rosters = relationship("Roster", back_populates="team")
    # TODO: this owners relationship requires more attention. is it many to many?
    # may need to change the ER Diagram and add a members tables as many to many.
    # there can be multiple members per team, but the other relationship is a
    # primary owner

    def __repr__(self):
        return (
            f"Team(id = {self.id!r},"
            f" season_id = {self.season_id!r},"
            f" primary_owner_id = {self.primary_owner_id!r},"
            f" espn_team_id = {self.espn_team_id!r},"
            f" team_name = {self.team_name!r},"
            f" abbrev = {self.abbrev!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
