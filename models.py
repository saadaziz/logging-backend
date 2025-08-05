from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from config import DB_URL

Base = declarative_base()

class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    service = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)

# Database setup
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def insert_log(service, level, message, context=None):
    session = SessionLocal()
    log = Log(service=service, level=level, message=message, context=context)
    session.add(log)
    session.commit()
    session.close()
