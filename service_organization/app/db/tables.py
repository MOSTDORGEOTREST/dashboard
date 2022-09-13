from sqlalchemy import Column, Date, Float, String, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Staff(Base):
    __tablename__ = 'Staff'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    password_hash = Column(String)
    phone_number = Column(BigInteger, nullable=True)
    birthday = Column(Date)
    is_superuser = Column(Boolean)
    rate = Column(Integer)
    developer_percent = Column(Float)
    calculation_percent = Column(Float)

class Work(Base):
    __tablename__ = 'Work'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Staff.id'))
    date = Column(Date)
    object_number = Column(String)
    work_id = Column(String, ForeignKey('WorkType.id'))
    count = Column(Float)

class WorkType(Base):
    __tablename__ = 'WorkType'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    work_name = Column(String)
    price = Column(Float)
    dev_tips = Column(Float)

class Prize(Base):
    __tablename__ = 'Prize'

    date = Column(Date, primary_key=True)
    value = Column(Float)
