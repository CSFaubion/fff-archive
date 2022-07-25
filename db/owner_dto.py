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


    teams = relationship("Team", back_populates="primary_owner")

    def __repr__(self):
        return (
            f"Owner(id={self.id!r}"
            f", first_name={self.first_name!r}"
            f", last_name={self.last_name!r}"
            f", espn_owner_id={self.espn_owner_id!r}"
            f", display_name={self.display_name!r})"
        )


if __name__ == "__main__":
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", echo=True, future=True)
    Base.metadata.create_all(engine)
