import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/data.db')
engine = create_engine(
    url=f'sqlite:///{database_path}',
)

print(database_path)

SessionLocal = sessionmaker(engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
