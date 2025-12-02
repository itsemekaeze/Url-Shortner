from src.database.core import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship





class ClickModel(Base):
    __tablename__ = "clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    referer = Column(String(2048), nullable=True)
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    
    url = relationship("URLModel", back_populates="clicks")
