from db.database import get_db


class Flashcard:
    def __init__(self, id, deck_id, front, back, created_at=None):
        self.id = id
        self.deck_id = deck_id
        self.front = front
        self.back = back
        self.created_at = created_at

    @classmethod
    def create(cls, deck_id, front, back):
        """Create a new flashcard and return the Flashcard instance."""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO flashcards (deck_id, front, back) VALUES (%s, %s, %s) RETURNING id',
            (deck_id, front, back)
        )
        card_id = cursor.fetchone()['id']
        db.commit()
        return cls.get_by_id(card_id)

    @classmethod
    def get_by_id(cls, card_id):
        """Fetch a flashcard by its primary key. Returns Flashcard or None."""
        db = get_db()
        row = db.execute('SELECT * FROM flashcards WHERE id = %s', (card_id,)).fetchone()
        if row is None:
            return None
        return cls(
            id=row['id'],
            deck_id=row['deck_id'],
            front=row['front'],
            back=row['back'],
            created_at=row['created_at']
        )

    def update(self, front, back):
        """Update the flashcard's front and back text."""
        db = get_db()
        db.execute(
            'UPDATE flashcards SET front = %s, back = %s WHERE id = %s',
            (front, back, self.id)
        )
        db.commit()
        self.front = front
        self.back = back

    def delete(self):
        """Delete this flashcard from the database."""
        db = get_db()
        db.execute('DELETE FROM flashcards WHERE id = %s', (self.id,))
        db.commit()
