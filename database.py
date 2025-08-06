from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class CaseQuery(Base):
    __tablename__ = 'case_queries'
    
    id = Column(Integer, primary_key=True)
    case_type = Column(String(50))
    case_number = Column(String(50))
    filing_year = Column(Integer)
    query_time = Column(DateTime, default=datetime.utcnow)
    raw_response = Column(Text)  # Store the complete HTML response
    status = Column(String(20))  # 'success', 'failed', 'pending'
    parties = Column(Text)       # Store parties information as JSON string
    dates = Column(Text)         # Store dates information as JSON string
    pdf_links = Column(Text)     # Store PDF links as JSON string
    
    def __repr__(self):
        return f"<CaseQuery({self.case_type}/{self.case_number}/{self.filing_year})>"


def init_db():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal
