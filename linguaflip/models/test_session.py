from db.database import get_db


class TestSession:
    def __init__(self, id, user_id, deck_id, score, total, taken_at=None):
        self.id = id
        self.user_id = user_id
        self.deck_id = deck_id
        self.score = score
        self.total = total
        self.taken_at = taken_at

    @classmethod
    def create(cls, user_id, deck_id, total):
        """Create a new test session with score=0 and return the TestSession instance."""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO test_sessions (user_id, deck_id, score, total) '
            'VALUES (%s, %s, 0, %s) RETURNING *',
            (user_id, deck_id, total)
        )
        row = cursor.fetchone()
        db.commit()
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            deck_id=row['deck_id'],
            score=row['score'],
            total=row['total'],
            taken_at=row['taken_at']
        )

    def update_score(self, score):
        """Update the score for this test session."""
        db = get_db()
        db.execute('UPDATE test_sessions SET score = %s WHERE id = %s', (score, self.id))
        db.commit()
        self.score = score

    @classmethod
    def get_history_for_deck(cls, deck_id, user_id):
        """Return all test sessions for a deck/user, ordered by most recent first."""
        db = get_db()
        rows = db.execute(
            'SELECT * FROM test_sessions WHERE deck_id = %s AND user_id = %s ORDER BY taken_at DESC',
            (deck_id, user_id)
        ).fetchall()
        return [
            cls(
                id=row['id'],
                user_id=row['user_id'],
                deck_id=row['deck_id'],
                score=row['score'],
                total=row['total'],
                taken_at=row['taken_at']
            )
            for row in rows
        ]
