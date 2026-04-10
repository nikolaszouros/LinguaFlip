import bcrypt
from db.database import get_db


class User:
    def __init__(self, id, username, email, password_hash, native_lang, created_at=None, profile_pic=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.native_lang = native_lang
        self.created_at = created_at
        self.profile_pic = profile_pic

    @classmethod
    def _from_row(cls, row):
        return cls(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            native_lang=row['native_lang'],
            created_at=row['created_at'],
            profile_pic=row.get('profile_pic'),
        )

    @classmethod
    def register(cls, username, email, password, native_lang):
        db = get_db()
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        cursor = db.execute(
            'INSERT INTO users (username, email, password_hash, native_lang) '
            'VALUES (%s, %s, %s, %s) RETURNING id',
            (username, email, password_hash, native_lang)
        )
        user_id = cursor.fetchone()['id']
        db.commit()
        return cls.get_by_id(user_id)

    @classmethod
    def authenticate(cls, username_or_email, password):
        """Verify credentials. Returns User on success, None on failure."""
        db = get_db()
        row = db.execute(
            'SELECT * FROM users WHERE username = %s OR email = %s',
            (username_or_email, username_or_email)
        ).fetchone()
        if row is None:
            return None
        stored_hash = row['password_hash']
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        if not bcrypt.checkpw(password.encode(), stored_hash):
            return None
        return cls._from_row(row)

    @classmethod
    def get_by_id(cls, user_id):
        db = get_db()
        row = db.execute('SELECT * FROM users WHERE id = %s', (user_id,)).fetchone()
        return cls._from_row(row) if row else None

    def get_decks(self):
        from models.deck import Deck
        return Deck.get_all_for_user(self.id)

    def get_ai_usage_today(self):
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM ai_usage_log "
            "WHERE user_id = %s AND requested_at >= NOW() - INTERVAL '24 hours'",
            (self.id,)
        ).fetchone()
        return row['cnt'] if row else 0
