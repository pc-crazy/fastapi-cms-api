# # src/init_db.py
# import asyncio
# from src.database import Base, engine
#
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#         print("✅ Database tables created successfully.")
#
# if __name__ == "__main__":
#     asyncio.run(init_db())
