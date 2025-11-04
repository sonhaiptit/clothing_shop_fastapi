"""Database connection and utilities."""
import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': settings.db_host,
    'user': settings.db_user,
    'password': settings.db_password,
    'database': settings.db_name,
    'charset': settings.db_charset
}

# Connection pool
connection_pool: Optional[pooling.MySQLConnectionPool] = None


def init_connection_pool():
    """Initialize database connection pool."""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="clothing_shop_pool",
            pool_size=5,
            pool_reset_session=True,
            **DB_CONFIG
        )
        logger.info("Database connection pool initialized successfully")
    except Error as e:
        logger.error(f"Error creating connection pool: {e}")
        connection_pool = None


def get_db_connection():
    """Get database connection from pool or create new connection."""
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
            return connection
        else:
            # Fallback to direct connection if pool is not available
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None
