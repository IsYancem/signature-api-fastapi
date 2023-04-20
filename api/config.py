import os

SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key_here"
ALGORITHM = "HS256"