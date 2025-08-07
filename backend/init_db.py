#!/usr/bin/env python3
"""Initialize database with tables"""

import asyncio
from sqlalchemy import text
from app.database import async_engine, Base
from app.models import *  # Import all models

async def init_db():
    """Create all tables in the database"""
    async with async_engine.begin() as conn:
        # Create schema if needed
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        
        # Drop all tables (for development only)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())