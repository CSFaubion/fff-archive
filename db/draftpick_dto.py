from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship
from base import Base


class Draftpick(Base):
    __tablename__ = 'Draftpicks'

    id = Column(Integer, primary_key=True)

    team_id = Column(Integer)  # TODO:foreign key?
    player_id = Column(Integer, ForeignKey('Players.id'))

    round_number = Column(Integer)
    round_pick = Column(Integer)
    pick_number = Column(Integer)
    bid_amount = Column(Integer)
    keeper_status = Column(Boolean)

    player = relationship("Player", back_populates="draftpicks")

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
