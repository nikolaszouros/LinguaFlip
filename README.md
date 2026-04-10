# LinguaFlip

A web-based language learning platform for building vocabulary through flashcards. Create custom decks, study with interactive flip cards, test yourself with timed quizzes, and use AI to generate vocabulary suggestions — all tracked with personal progress stats.

---

## Features

- **Deck Management** — Create and manage language learning decks with a source and target language
- **Flashcard CRUD** — Add, edit, and delete cards within any deck
- **Study Mode** — Interactive flip-card interface with keyboard shortcuts (Space/F to flip, arrow keys or H/L to navigate)
- **Test Mode** — Shuffled quiz where you type answers; case-insensitive scoring with detailed results
- **AI Vocabulary Suggestions** — Uses the Google Gemini API to suggest relevant word pairs for your language pair; rate-limited to 10 requests per user per 24 hours
- **AI Translation** — Translate a single word on the fly while adding a new card
- **Dashboard** — View total decks and cards, test history (last 20 sessions), streak tracking, and best scores
- **User Profiles** — Upload a profile picture, set your native language, and view personal statistics
- **Secure Authentication** — Registration and login with bcrypt password hashing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+, Flask 3.0 |
| Database | PostgreSQL (via psycopg 3) |
| Templates | Jinja2 |
| Frontend | Vanilla HTML, CSS, JavaScript (no frameworks) |
| AI | Google Gemini API |
| Auth | bcrypt |
| Testing | pytest |

---

## Prerequisites

- Python 3.8+
- PostgreSQL
- A Google Gemini API key (optional — only required for AI features)

---

## Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/nikolaszouros/flashcard_language_game.git
cd flashcard_language_game/linguaflip

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
#    Create a file named .env inside the linguaflip/ directory:

SECRET_KEY=<long random string>
DATABASE_URL=postgresql://user:password@localhost:5432/LinguaFlip
GEMINI_API_KEY=<your Gemini API key>   # optional

#    Generate a secret key with:
#    python -c "import secrets; print(secrets.token_hex(32))"

# 5. Create the database
#    In psql (or pgAdmin), create a database named LinguaFlip.
#    The schema is applied automatically on first run.

# 6. Run the application
python app.py
```

Open your browser at **http://127.0.0.1:5000**.

---

## Running Tests

```bash
cd linguaflip
pytest
```

Tests use an isolated in-memory database and do not touch your production data.

---

## Project Structure

```
flashcard_language_game/
└── linguaflip/
    ├── app.py                  # Flask app factory and root routes
    ├── requirements.txt
    ├── .env                    # Local secrets (not committed)
    ├── db/
    │   ├── database.py         # PostgreSQL connection wrapper
    │   └── schema.sql          # Table definitions
    ├── models/                 # Raw SQL data access (no ORM)
    │   ├── user.py
    │   ├── deck.py
    │   ├── flashcard.py
    │   └── test_session.py
    ├── routes/                 # Flask blueprints
    │   ├── auth.py             # /auth  — login, register, logout
    │   ├── decks.py            # /decks — deck CRUD, dashboard
    │   ├── cards.py            # /cards — card CRUD, translate
    │   ├── study.py            # /study — flip-card study mode
    │   ├── test.py             # /test  — typed-answer quiz mode
    │   ├── ai.py               # /ai    — vocabulary suggestions
    │   └── profile.py          # /profile — user settings
    ├── services/
    │   └── ai_service.py       # Gemini API wrapper with rate limiting
    ├── templates/              # Jinja2 HTML templates
    ├── static/
    │   ├── css/style.css
    │   ├── js/
    │   │   ├── flashcard.js    # Flip animation, keyboard navigation
    │   │   └── test.js         # Quiz logic, answer submission, results
    │   └── uploads/profiles/   # User profile pictures
    └── tests/
```

---

## How It Works

1. **Register / Log in** to create an account.
2. **Create a deck** and give it a source and target language (e.g. English → Spanish).
3. **Add flashcards** manually, or use the AI suggestion tool to generate a batch of vocabulary words for your language pair.
4. **Study** your deck in flip-card mode — cards are shown front-side up, click or press Space to reveal the answer, and use the arrow keys to move between cards.
5. **Take a test** — cards are shuffled and you type the target-language answer for each. Your score is recorded and tracked on your dashboard.
6. **Track progress** on the dashboard: see your current streak, best scores, and a full history of past test sessions.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Random secret for Flask session encryption |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GEMINI_API_KEY` | No | Google Gemini API key for AI features |

---

## License

This project does not currently include a license file.
