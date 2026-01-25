"""Database schema management and migrations."""

from sqlalchemy import inspect
from .database import get_db_config
from .models import Base


class SchemaManager:
    """Manage database schema creation and migrations."""
    
    @staticmethod
    def create_all_tables() -> None:
        """Create all tables in the database."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        Base.metadata.create_all(bind=db_config.engine)
    
    @staticmethod
    def drop_all_tables() -> None:
        """Drop all tables from the database (WARNING: destructive operation)."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        Base.metadata.drop_all(bind=db_config.engine)
    
    @staticmethod
    def table_exists(table_name: str) -> bool:
        """Check if a table exists in the database."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        inspector = inspect(db_config.engine)
        return table_name in inspector.get_table_names()
    
    @staticmethod
    def get_all_tables() -> list:
        """Get all table names in the database."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        inspector = inspect(db_config.engine)
        return inspector.get_table_names()
    
    @staticmethod
    def get_table_info(table_name: str) -> dict:
        """Get information about a specific table."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        
        inspector = inspect(db_config.engine)
        if table_name not in inspector.get_table_names():
            return {}
        
        return {
            "columns": inspector.get_columns(table_name),
            "indexes": inspector.get_indexes(table_name),
            "primary_key": inspector.get_pk_constraint(table_name),
            "foreign_keys": inspector.get_foreign_keys(table_name),
        }
    
    @staticmethod
    def get_database_stats() -> dict:
        """Get overall database statistics."""
        db_config = get_db_config()
        if db_config.engine is None:
            raise RuntimeError("Database not initialized")
        
        inspector = inspect(db_config.engine)
        tables = inspector.get_table_names()
        
        stats = {
            "total_tables": len(tables),
            "tables": {}
        }
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            stats["tables"][table_name] = {
                "column_count": len(columns),
                "columns": [col["name"] for col in columns]
            }
        
        return stats
