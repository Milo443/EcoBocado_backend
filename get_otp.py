from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def get_latest_otp(email):
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    server = os.getenv("POSTGRES_SERVER")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    db_url = f"postgresql://{user}:{password}@{server}:{port}/{db}"
    engine = create_engine(db_url)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT otp_code, created_at 
            FROM otps 
            WHERE email = :email 
            ORDER BY created_at DESC 
            LIMIT 1
        """), {"email": email}).first()
        
        if result:
            print(f"\n[OTP] Para: {email}")
            print(f"Código: {result[0]}")
            print(f"Creado hace: {result[1]}")
        else:
            print(f"\nNo se encontró OTP para {email}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python get_otp.py <email>")
    else:
        get_latest_otp(sys.argv[1])
