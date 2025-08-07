import os
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv("SECRET_KEY")

print(f"Hello from aws_ai_scholar!")
print(f"Loaded secret key: {secret}")
