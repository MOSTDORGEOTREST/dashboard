from sqlalchemy import Column, Date, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Reports(Base):
    __tablename__ = 'Reports'

    id = Column(String, primary_key=True)
    date = Column(Date)
    object_number = Column(String)
    object_name = Column(String)
    laboratory_number = Column(String)
    test_type = Column(String)

