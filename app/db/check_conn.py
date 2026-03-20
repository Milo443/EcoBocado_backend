import asyncio
from sqlalchemy import text
from app.db.bd_conections import DatabaseManager

def _sync_check_db() -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True

async def check_db_connection() -> bool:
    try:
        # Initialize pools first
        DatabaseManager.initialize_pools()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(DatabaseManager.executor, _sync_check_db)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    async def main():
        success = await check_db_connection()
        if success:
            print("Successfully connected to the database!")
        else:
            print("Failed to connect to the database.")
        DatabaseManager.shutdown()

    asyncio.run(main())
