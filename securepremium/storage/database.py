"""Database configuration and session management."""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Database URL configuration
DEFAULT_DB_URL = os.getenv("DATABASE_URL", "sqlite:///securepremium.db")


class DatabaseConfig:
    """Database configuration manager."""
    
    def __init__(self, db_url: str = DEFAULT_DB_URL):
        """
        Initialize database configuration.
        
        Args:
            db_url: Database connection URL
        """
        self.db_url = db_url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
    
    def initialize(self) -> None:
        """Initialize database connection and session factory."""
        # Use StaticPool for SQLite to avoid threading issues
        if self.db_url.startswith("sqlite://"):
            self.engine = create_engine(
                self.db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(
                self.db_url,
                echo=False,
                pool_pre_ping=True,  # Verify connections before using
            )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy session object
            
        Raises:
            RuntimeError: If database not initialized
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()


# Global database configuration
_db_config: Optional[DatabaseConfig] = None


def get_db_config() -> DatabaseConfig:
    """Get global database configuration instance."""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
        _db_config.initialize()
    return _db_config


def init_db(db_url: str = DEFAULT_DB_URL) -> DatabaseConfig:
    """
    Initialize database with custom URL.
    
    Args:
        db_url: Database connection URL
        
    Returns:
        Configured DatabaseConfig instance
    """
    global _db_config
    _db_config = DatabaseConfig(db_url)
    _db_config.initialize()
    return _db_config
