"""Script to test database connectivity and initialize tables."""

import asyncio
import sys

from sqlalchemy import text

from jemini.storage.database import engine, init_db


async def check_and_init():
    print("Testing connection to PostgreSQL...")
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version();"))
            row = res.fetchone()
            print(f"Connected to PostgreSQL: {row[0]}")
            
            # Check vector extension
            vec_res = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            vec_row = vec_res.fetchone()
            if vec_row:
                print("✓ pgvector extension is ENABLED")
            else:
                print("! pgvector extension not found, attempting to create...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                print("✓ pgvector extension created.")

        print("Creating Jemini database tables (AgentMemory, ChannelAuditLog)...")
        await init_db()
        print("✓ All tables initialized successfully!")

    except Exception as e:  # noqa: BLE001
        print(f"Connection error: {e}", file=sys.stderr)
        print("\nMake sure Docker Desktop is started and 'docker compose up -d' has been executed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_and_init())
