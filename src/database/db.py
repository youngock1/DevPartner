import asyncio
import asyncpg

async def main():

    conn = await asyncpg.connect(
        user='user',
        password='password',
        database='database',
        host='localhost',
        port=5432
    )
