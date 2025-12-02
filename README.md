# URL Shortener API

A modern, production-ready URL shortener service built with FastAPI and SQLAlchemy. Create short, memorable links with analytics, custom aliases, and expiration dates.

## Features

- ✂️ **URL Shortening**: Convert long URLs into short, shareable links
- 🎯 **Custom Aliases**: Create memorable custom short codes
- 📊 **Analytics**: Track clicks, referrers, and user agents
- ⏰ **Expiration Dates**: Set automatic link expiration
- 🔗 **RESTful API**: Clean, well-documented API endpoints
- 🗄️ **Database Backed**: Persistent storage with SQLAlchemy
- 🚀 **Fast & Async**: Built on FastAPI for high performance

## Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation
- **SQLite/PostgreSQL** - Database (configurable)

## Installation

### Prerequisites

- Python 3.8+
- pip or poetry

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd url-shortener
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=sqlite:///./url_shortener.db
# For PostgreSQL: postgresql://user:password@localhost/dbname
```

Create a `.env.example` file for reference:
```env
DATABASE_URL=your_database_url_here
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Create Short URL

**POST** `/api/v1/shorten`

Create a new shortened URL with optional custom alias and expiration.

**Request Body:**
```json
{
  "original_url": "https://www.example.com/very/long/url/path",
  "custom_alias": "mylink",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response (201):**
```json
{
  "id": 1,
  "original_url": "https://www.example.com/very/long/url/path",
  "short_code": "mylink",
  "short_url": "http://localhost:8000/mylink",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "click_count": 0
}
```

#### 2. Redirect to Original URL

**GET** `/{short_code}`

Redirects to the original URL and tracks the click.

**Example:**
```
GET http://localhost:8000/mylink
→ Redirects to https://www.example.com/very/long/url/path
```

#### 3. Get URL Statistics

**GET** `/api/v1/urls/{short_code}/stats`

Retrieve analytics for a shortened URL.

**Response (200):**
```json
{
  "id": 1,
  "original_url": "https://www.example.com/very/long/url/path",
  "short_code": "mylink",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z",
  "click_count": 42,
  "last_accessed": "2024-01-16T14:20:00Z",
  "recent_clicks": [
    {
      "id": 1,
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "referer": "https://twitter.com",
      "clicked_at": "2024-01-16T14:20:00Z"
    }
  ]
}
```

#### 4. List All URLs

**GET** `/api/v1/urls?skip=0&limit=100`

Get a paginated list of all shortened URLs.

**Query Parameters:**
- `skip` (default: 0) - Number of records to skip
- `limit` (default: 100) - Maximum number of records to return

#### 5. Delete URL

**DELETE** `/api/v1/urls/{short_code}`

Delete a shortened URL and all associated analytics.

**Response:** `204 No Content`

## Usage Examples

### Using cURL

**Create a short URL:**
```bash
curl -X POST "http://localhost:8000/api/v1/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://github.com/fastapi/fastapi",
    "custom_alias": "fastapi"
  }'
```

**Get statistics:**
```bash
curl "http://localhost:8000/api/v1/urls/fastapi/stats"
```

### Using Python

```python
import requests

# Create short URL
response = requests.post(
    "http://localhost:8000/api/v1/shorten",
    json={
        "original_url": "https://github.com/fastapi/fastapi",
        "custom_alias": "fastapi"
    }
)
data = response.json()
print(f"Short URL: {data['short_url']}")

# Get statistics
stats = requests.get(f"http://localhost:8000/api/v1/urls/fastapi/stats")
print(f"Clicks: {stats.json()['click_count']}")
```

### Using JavaScript/Fetch

```javascript
// Create short URL
const response = await fetch('http://localhost:8000/api/v1/shorten', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    original_url: 'https://github.com/fastapi/fastapi',
    custom_alias: 'fastapi'
  })
});

const data = await response.json();
console.log('Short URL:', data.short_url);
```

## Project Structure

```
url-shortener/
├── main.py                 # Application entry point
├── src/
│   ├── database/
│   │   └── core.py        # Database configuration
│   ├── entities/
│   │   ├── url.py         # URL model
│   │   └── click.py       # Click analytics model
│   ├── schemas/
│   │   └── models.py      # Pydantic schemas
│   └── utils.py           # Helper functions
├── .env                   # Environment variables (create this)
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Configuration

### Database

The application uses SQLite by default. To use PostgreSQL:

1. Install the PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update your `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost/url_shortener
```

### Custom Short Code Length

Modify the `generate_short_code()` function in `src/utils.py`:
```python
def generate_short_code(length: int = 8) -> str:  # Change default length
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid URL format or custom alias |
| 404 | Short URL not found |
| 409 | Custom alias already exists |
| 410 | Short URL has expired |
| 500 | Server error |

## Development

### Run with auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests

```bash
pytest tests/
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:password@db-host:5432/url_shortener
HOST=0.0.0.0
PORT=8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI framework
- SQLAlchemy ORM
- The Python community

## Support

For issues and questions:
- Create an issue on GitHub
- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review the API docs at `/docs`

---

**Built with ❤️ using FastAPI**