# main.py
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uvicorn
from src.database.core import engine, get_db, Base
from src.entities.click import ClickModel  
from src.entities.url import URLModel
from src.schemas.models import URLCreate, URLResponse, URLStats, ClickResponse
from src.utils import generate_short_code, is_valid_url


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="Shorten URLs with analytics and custom aliases",
    version="1.0.0"
)


@app.post("/api/v1/shorten", response_model=URLResponse, status_code=201)
async def create_short_url(
    url_data: URLCreate,
    request: Request,
    db: Session = Depends(get_db)
):
   
    if not is_valid_url(url_data.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    
    if url_data.custom_alias:
        
        if len(url_data.custom_alias) < 3 or len(url_data.custom_alias) > 20:
            raise HTTPException(
                status_code=400,
                detail="Custom alias must be between 3 and 20 characters"
            )
        
      
        existing = db.query(URLModel).filter(URLModel.short_code == url_data.custom_alias).first()
        if existing:
            raise HTTPException(status_code=409, detail="Custom alias already exists")
        
        short_code = url_data.custom_alias
    else:
       
        max_attempts = 10
        for _ in range(max_attempts):
            short_code = generate_short_code()
            existing = db.query(URLModel).filter(URLModel.short_code == short_code).first()
            if not existing:
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique short code")
    
    
    db_url = URLModel(
        original_url=url_data.original_url,
        short_code=short_code,
        expires_at=url_data.expires_at
    )
    
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    
    base_url = str(request.base_url).rstrip('/')
    short_url = f"{base_url}/{short_code}"
    
    return URLResponse(
        id=db_url.id,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=short_url,
        created_at=db_url.created_at,
        expires_at=db_url.expires_at,
        click_count=db_url.click_count
    )


@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    url_entry = db.query(URLModel).filter(URLModel.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    
    if url_entry.expires_at:
        now = datetime.now(timezone.utc)
        expires = url_entry.expires_at
       
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires < now:
            raise HTTPException(status_code=410, detail="Short URL has expired")
    
    
    click = ClickModel(
        url_id=url_entry.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "Unknown"),
        referer=request.headers.get("referer")
    )
    
    
    url_entry.click_count += 1
    url_entry.last_accessed = datetime.now(timezone.utc)
    
    db.add(click)
    db.commit()
    
    
    return RedirectResponse(url=url_entry.original_url, status_code=307)


@app.get("/api/v1/urls/{short_code}/stats", response_model=URLStats)
async def get_url_stats(short_code: str, db: Session = Depends(get_db)):
   
    
    url_entry = db.query(URLModel).filter(URLModel.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    
    recent_clicks = (
        db.query(ClickModel)
        .filter(ClickModel.url_id == url_entry.id)
        .order_by(ClickModel.clicked_at.desc())
        .limit(10)
        .all()
    )
    
    clicks_data = [
        ClickResponse(
            id=click.id,
            ip_address=click.ip_address,
            user_agent=click.user_agent,
            referer=click.referer,
            clicked_at=click.clicked_at
        )
        for click in recent_clicks
    ]
    
    return URLStats(
        id=url_entry.id,
        original_url=url_entry.original_url,
        short_code=url_entry.short_code,
        created_at=url_entry.created_at,
        expires_at=url_entry.expires_at,
        click_count=url_entry.click_count,
        last_accessed=url_entry.last_checked,
        recent_clicks=clicks_data
    )


@app.get("/api/v1/urls", response_model=list[URLResponse])
async def list_urls(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    urls = db.query(URLModel).offset(skip).limit(limit).all()
    
    url_list = []
    for url in urls:
        url_list.append(URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"/{url.short_code}",
            created_at=url.created_at,
            expires_at=url.expires_at,
            click_count=url.click_count
        ))
    
    return url_list


@app.delete("/api/v1/urls/{short_code}", status_code=204)
async def delete_url(short_code: str, db: Session = Depends(get_db)):
    
    url_entry = db.query(URLModel).filter(URLModel.short_code == short_code).first()
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    db.delete(url_entry)
    db.commit()
    
    return Response(status_code=204)


@app.get("/")
async def root():
    
    return {
        "message": "URL Shortener API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "shorten": "POST /api/v1/shorten",
            "redirect": "GET /{short_code}",
            "stats": "GET /api/v1/urls/{short_code}/stats",
            "list": "GET /api/v1/urls",
            "delete": "DELETE /api/v1/urls/{short_code}"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)