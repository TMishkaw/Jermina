import asyncio

from jemini.storage.database import engine
from jemini.storage.models import Base


async def init_tables():
    async with engine.begin() as conn:
        print("Creating all tables from Base (including YouTube tables)...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_tables())
