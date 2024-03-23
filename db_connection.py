from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

engine = create_engine(
    url='sqlite:///C:\Projects\TeleBots\Bots_in_work\sof_jk_bot\sof_jk_bot\db\data.db',
)
SessionLocal = sessionmaker(engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
