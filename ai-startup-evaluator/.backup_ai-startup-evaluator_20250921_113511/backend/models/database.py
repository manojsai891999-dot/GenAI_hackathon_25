from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from cloudsql_config import get_cloudsql_connection_string
    DATABASE_URL = get_cloudsql_connection_string()
except ImportError:
    # Fallback configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./startup_evaluator.db"  # Default to SQLite for local development
    )

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=True if os.getenv("DEBUG") == "true" else False
    )
elif "cloudsql" in DATABASE_URL:
    # CloudSQL configuration
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Use NullPool for Cloud SQL
        echo=True if os.getenv("DEBUG") == "true" else False,
        # CloudSQL specific connection args
        connect_args={
            "sslmode": "disable"  # CloudSQL handles SSL internally
        }
    )
else:
    # Standard PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Use NullPool for Cloud SQL
        echo=True if os.getenv("DEBUG") == "true" else False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()
metadata = MetaData()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Drop all tables (for development)
def drop_tables():
    Base.metadata.drop_all(bind=engine)
