from db.database import get_db


class Deck:
    def __init__(self, id, user_id, name, source_lang, target_lang, created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.created_at = created_at

    @classmethod
    def create(cls, user_id, name, source_lang, target_lang):
        """Create a new deck and return the Deck instance."""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO decks (user_id, name, source_lang, target_lang) '
            'VALUES (%s, %s, %s, %s) RETURNING id',
            (user_id, name, source_lang, target_lang)
        )
        deck_id = cursor.fetchone()['id']
        db.commit()
        return cls.get_by_id(deck_id)

    @classmethod
    def get_by_id(cls, deck_id, user_id=None):
        """Fetch a deck by ID, optionally filtering by user_id for ownership checks."""
        db = get_db()
        if user_id is not None:
            row = db.execute(
                'SELECT * FROM decks WHERE id = %s AND user_id = %s',
                (deck_id, user_id)
            ).fetchone()
        else:
            row = db.execute('SELECT * FROM decks WHERE id = %s', (deck_id,)).fetchone()
        if row is None:
            return None
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            name=row['name'],
            source_lang=row['source_lang'],
            target_lang=row['target_lang'],
            created_at=row['created_at']
        )

    @classmethod
    def get_all_for_user(cls, user_id):
        """Return all decks belonging to the given user, ordered by creation date."""
        db = get_db()
        rows = db.execute(
            'SELECT * FROM decks WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()
        return [
            cls(
                id=row['id'],
                user_id=row['user_id'],
                name=row['name'],
                source_lang=row['source_lang'],
                target_lang=row['target_lang'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def update(self, name):
        """Update the deck's name."""
        db = get_db()
        db.execute('UPDATE decks SET name = %s WHERE id = %s', (name, self.id))
        db.commit()
        self.name = name

    def delete(self):
        """Delete the deck (cascades to flashcards and test sessions)."""
        db = get_db()
        db.execute('DELETE FROM decks WHERE id = %s', (self.id,))
        db.commit()

    def get_cards(self):
        """Return a list of Flashcard objects belonging to this deck."""
        from models.flashcard import Flashcard
        db = get_db()
        rows = db.execute(
            'SELECT * FROM flashcards WHERE deck_id = %s ORDER BY created_at ASC',
            (self.id,)
        ).fetchall()
        return [
            Flashcard(
                id=row['id'],
                deck_id=row['deck_id'],
                front=row['front'],
                back=row['back'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_stats(self):
        """Return a dict with card_count, test_count, best_score, last_score."""
        db = get_db()
        card_count_row = db.execute(
            'SELECT COUNT(*) AS cnt FROM flashcards WHERE deck_id = %s',
            (self.id,)
        ).fetchone()
        card_count = card_count_row['cnt'] if card_count_row else 0

        test_rows = db.execute(
            'SELECT score, total FROM test_sessions WHERE deck_id = %s ORDER BY taken_at DESC',
            (self.id,)
        ).fetchall()

        test_count = len(test_rows)
        best_score = None
        last_score = None

        if test_rows:
            last_row = test_rows[0]
            last_score = round(last_row['score'] / last_row['total'] * 100) if last_row['total'] > 0 else 0

            best_pct = 0
            for row in test_rows:
                if row['total'] > 0:
                    pct = row['score'] / row['total'] * 100
                    if pct > best_pct:
                        best_pct = pct
            best_score = round(best_pct)

        return {
            'card_count': card_count,
            'test_count': test_count,
            'best_score': best_score,
            'last_score': last_score
        }
