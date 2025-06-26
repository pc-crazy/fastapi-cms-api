# tests/test_database.py

import pytest
import pytest_asyncio
from src.database import get_db

@pytest.mark.asyncio
async def test_get_db_lifecycle():
    db_gen = get_db()
    db = await anext(db_gen)
    assert db is not None
    assert db.is_active is True
    try:
        await anext(db_gen)  # Trigger finally block
    except StopAsyncIteration:
        pass
