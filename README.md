# LinguaFlip

LinguaFlip is a Flask-based web application for learning vocabulary through interactive flashcards. Build custom decks, study with animated flashcards, take typed-answer tests, and get AI-generated word suggestions powered by Claude.

---

## Features

- **User accounts** — register, log in, and log out with bcrypt-hashed passwords.
- **Decks** — create, edit, and delete flashcard decks with a source and target language.
- **Flashcards** — add, edit, and delete cards with front (source) and back (translation) text.
- **Study mode** — flip through cards one at a time using a CSS 3D flip animation; keyboard shortcuts supported.
- **Test mode** — type answers to each card; results are scored and saved to history.
- **Dashboard** — view total decks, total cards, recent test history, and your day streak.
- **AI suggestions** — generate 5–10 vocabulary words for any deck using the Anthropic Claude API (rate-limited to 10 requests per 24 hours per user).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.0 |
| Database | SQLite (via Python stdlib `sqlite3`) |
| Password hashing | bcrypt |
| AI integration | Anthropic Claude (claude-haiku-4-5) |
| Environment config | python-dotenv |
| Testing | pytest |
| Frontend | Vanilla HTML / CSS / JavaScript |

---

## How to Run

### 1. Clone / navigate to the project

```bash
cd linguaflip
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\Activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)

Create a `.env` file in the `linguaflip/` directory:

```dotenv
SECRET_KEY=change-me-in-production
DATABASE_PATH=linguaflip.db
ANTHROPIC_API_KEY=sk-ant-...
```

If `ANTHROPIC_API_KEY` is not set, the application runs normally but AI suggestions return a friendly error message.

### 5. Run the development server

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Running Tests

```bash
cd linguaflip
pytest tests/ -v
```

Tests use an in-memory SQLite database so they are fully isolated and leave no files on disk.

---

## Project Structure

```
linguaflip/
├── app.py                  # Flask application factory
├── requirements.txt
├── README.md
├── db/
│   ├── __init__.py
│   ├── database.py         # Singleton DB connection helpers
│   └── schema.sql          # Table definitions & indexes
├── models/
│   ├── __init__.py
│   ├── user.py             # User model (register, authenticate, …)
│   ├── deck.py             # Deck model (CRUD, stats)
│   ├── flashcard.py        # Flashcard model (CRUD)
│   └── test_session.py     # TestSession model
├── services/
│   ├── __init__.py
│   └── ai_service.py       # Anthropic API wrapper + rate limiting
├── routes/
│   ├── __init__.py
│   ├── auth.py             # /auth — login, register, logout
│   ├── decks.py            # /decks — deck CRUD + dashboard
│   ├── cards.py            # /cards — flashcard CRUD
│   ├── study.py            # /study — study mode
│   ├── test.py             # /test — test mode + submit
│   └── ai.py               # /ai — suggest + add cards
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── decks/
│   │   ├── index.html
│   │   ├── new.html
│   │   ├── detail.html
│   │   └── edit.html
│   ├── cards/
│   │   ├── new.html
│   │   └── edit.html
│   ├── study/
│   │   └── index.html
│   ├── test/
│   │   ├── index.html
│   │   └── results.html
│   └── dashboard/
│       └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── flashcard.js    # Study mode (flip, prev, next)
│       └── test.js         # Test mode (submit, inline results)
└── tests/
    ├── __init__.py
    ├── conftest.py         # Shared fixtures (in-memory DB)
    ├── test_user.py
    ├── test_deck.py
    └── test_flashcard.py
```
