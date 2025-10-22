from asyncio import run

from connection import engine
from models import Base


async def create_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        print("Banco de dados e tabelas criados com sucesso! ")

if __name__ == '__main__':
    run(create_database())