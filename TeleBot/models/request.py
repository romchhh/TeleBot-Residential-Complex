from sqlalchemy import Integer, String, Column
from datetime import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'requests'

    user_id = Column(String)
    name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    dataCreate = Column(Integer, primary_key=True)
    phone = Column(String)
    street = Column(String)
    house = Column(String)
    apartment = Column(String)
    typeReq = Column(String)
    pcsQuests = Column(String)
    car = Column(String)
    timeQuests = Column(String)
    status = Column(String)
