from sqlalchemy import Column, Date, Float, String, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

import enum
class staff(Base):
    __tablename__ = 'staff'

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    password_hash = Column(String)
    phone_number = Column(BigInteger, nullable=True)
    birthday = Column(Date)
    is_superuser = Column(Boolean)
    rate = Column(Integer)
    developer_percent = Column(Float)

class works(Base):
    __tablename__ = 'works'

    work_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('staff.employee_id'))
    date = Column(Date)
    object_number = Column(String)
    worktype_id = Column(Integer, ForeignKey('worktypes.worktype_id'))
    count = Column(Float)

class worktypes(Base):
    __tablename__ = 'worktypes'

    worktype_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String)
    work_name = Column(String)
    price = Column(Float)
    dev_tips = Column(Float)

class prizes(Base):
    __tablename__ = 'prizes'

    date = Column(Date, primary_key=True)
    value = Column(Float)
