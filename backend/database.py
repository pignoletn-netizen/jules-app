import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLITE_DATABASE_URL = os.getenv("SQLITE_URL", "sqlite:///./mvb.db")
POSTGRES_DATABASE_URL = os.getenv("DATABASE_URL")

engine = None

if POSTGRES_DATABASE_URL:
    try:
        temp_engine = create_engine(POSTGRES_DATABASE_URL, pool_pre_ping=True)
        conn = temp_engine.connect()
        conn.close()
        engine = temp_engine
        print("Connected successfully to PostgreSQL database.")
    except Exception as e:
        print(f"Could not connect to PostgreSQL ({e}). Falling back to local SQLite.")
        engine = create_engine(
            SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
        )
else:
    engine = create_engine(
        SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
