import sqlalchemy
from sqlalchemy.orm import registry

engine = sqlalchemy.create_engine(
    "sqlite+pysqlite:///:memory:", echo=True, future=True)

mapper_registry = registry()
Base = mapper_registry.generate_base()
