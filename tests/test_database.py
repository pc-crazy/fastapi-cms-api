# tests/test_database.py

from app.database import get_db

def test_get_db_lifecycle():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    assert db.is_active is True
    try:
        next(db_gen)  # Trigger finally block
    except StopIteration:
        pass
