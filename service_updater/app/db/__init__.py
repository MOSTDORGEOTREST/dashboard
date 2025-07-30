from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import configs

engine = create_engine(
    configs.database_url
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)