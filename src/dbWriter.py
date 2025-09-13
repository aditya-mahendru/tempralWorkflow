import psycopg2

async def write_to_postgres_activity(query: str) -> str:
    DATABASE_URL = "postgresql://user:password@host:port/database" # Replace with your details
    try:
        async with await psycopg2.AsyncConnection.connect(DATABASE_URL) as aconn:
            async with aconn.cursor() as acur:
                # Example: Inserting data
                await acur.execute(
                    query
                )
            await aconn.commit()
        return "Data successfully written to PostgreSQL."
    except Exception as e:
        raise RuntimeError(f"Failed to write to PostgreSQL: {e}")