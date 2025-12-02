from src.database.core import Base
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class URLModel(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    last_checked = Column(DateTime, nullable=True)
    
    
    clicks = relationship("ClickModel", back_populates="url", cascade="all, delete-orphan")
    
