import sqlalchemy
from sqlalchemy.orm import registry

from base import Base
from season_dto import Season
from setting_dto import Setting
from player_dto import Player
from draftpick_dto import Draftpick


engine = sqlalchemy.create_engine(
    "sqlite+pysqlite:///:memory:", echo=True, future=True)

# mapper_registry = registry()
# Base = mapper_registry.generate_base()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
