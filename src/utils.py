import string
import random
import re
from urllib.parse import urlparse


def generate_short_code(length: int = 6) -> str:
   
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def is_valid_url(url: str) -> bool:
    
    
    url_pattern = re.compile(
        r'^https?://'  
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?'  
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False