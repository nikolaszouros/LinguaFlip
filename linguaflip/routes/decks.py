from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from models.deck import Deck
from models.test_session import TestSession
from db.database import get_db
from languages import LANGUAGES

decks = Blueprint('decks', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@decks.route('/')
@login_required
def index():
    user = g.current_user
    deck_list = Deck.get_all_for_user(user.id)
    decks_with_stats = []
    for deck in deck_list:
        stats = deck.get_stats()
        source_name = LANGUAGES.get(deck.source_lang, deck.source_lang)
        target_name = LANGUAGES.get(deck.target_lang, deck.target_lang)
        decks_with_stats.append({
            'deck': deck,
            'stats': stats,
            'source_name': source_name,
            'target_name': target_name
        })
    return render_template('decks/index.html', decks_with_stats=decks_with_stats, languages=LANGUAGES)


@decks.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    user = g.current_user
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        source_lang = request.form.get('source_lang', '').strip()
        target_lang = request.form.get('target_lang', '').strip()
        if not name:
            flash('Deck name is required.', 'error')
            return render_template('decks/new.html', languages=LANGUAGES)
        if not source_lang or not target_lang:
            flash('Please select both source and target languages.', 'error')
            return render_template('decks/new.html', languages=LANGUAGES)
        if source_lang == target_lang:
            flash('Source and target languages must be different.', 'error')
            return render_template('decks/new.html', languages=LANGUAGES)
        deck = Deck.create(user.id, name, source_lang, target_lang)
        flash(f'Deck "{deck.name}" created!', 'success')
        return redirect(url_for('decks.detail', deck_id=deck.id))
    return render_template('decks/new.html', languages=LANGUAGES)


@decks.route('/<int:deck_id>')
@login_required
def detail(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    cards = deck.get_cards()
    stats = deck.get_stats()
    history = TestSession.get_history_for_deck(deck_id, user.id)
    source_name = LANGUAGES.get(deck.source_lang, deck.source_lang)
    target_name = LANGUAGES.get(deck.target_lang, deck.target_lang)
    return render_template(
        'decks/detail.html',
        deck=deck,
        cards=cards,
        stats=stats,
        history=history,
        source_name=source_name,
        target_name=target_name
    )


@decks.route('/<int:deck_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Deck name is required.', 'error')
            return render_template('decks/edit.html', deck=deck)
        deck.update(name)
        flash('Deck updated.', 'success')
        return redirect(url_for('decks.detail', deck_id=deck.id))
    return render_template('decks/edit.html', deck=deck)


@decks.route('/<int:deck_id>/delete', methods=['POST'])
@login_required
def delete(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    deck_name = deck.name
    deck.delete()
    flash(f'Deck "{deck_name}" deleted.', 'success')
    return redirect(url_for('decks.index'))


@decks.route('/dashboard')
@login_required
def dashboard():
    import json
    user = g.current_user
    db = get_db()

    # Total cards across all decks
    row = db.execute(
        'SELECT COUNT(*) AS cnt FROM flashcards f '
        'JOIN decks d ON f.deck_id = d.id WHERE d.user_id = %s',
        (user.id,)
    ).fetchone()
    total_cards = row['cnt'] if row else 0

    # Total decks
    deck_count_row = db.execute(
        'SELECT COUNT(*) AS cnt FROM decks WHERE user_id = %s', (user.id,)
    ).fetchone()
    total_decks = deck_count_row['cnt'] if deck_count_row else 0

    # Test history across all decks (most recent 20)
    history_rows = db.execute(
        'SELECT ts.*, d.name AS deck_name FROM test_sessions ts '
        'JOIN decks d ON ts.deck_id = d.id '
        'WHERE ts.user_id = %s ORDER BY ts.taken_at DESC LIMIT 20',
        (user.id,)
    ).fetchall()

    history = []
    for row in history_rows:
        pct = round(row['score'] / row['total'] * 100) if row['total'] > 0 else 0
        history.append({
            'deck_name': row['deck_name'],
            'deck_id': row['deck_id'],
            'score': row['score'],
            'total': row['total'],
            'pct': pct,
            'taken_at': row['taken_at']
        })

    # Streak: consecutive days on which the user took at least one test
    streak_rows = db.execute(
        "SELECT DATE(taken_at) AS test_date FROM test_sessions "
        "WHERE user_id = %s GROUP BY DATE(taken_at) ORDER BY test_date DESC",
        (user.id,)
    ).fetchall()

    streak = 0
    if streak_rows:
        from datetime import date, timedelta
        today = date.today()
        expected = today
        for sr in streak_rows:
            d = date.fromisoformat(str(sr['test_date']))
            if d == expected:
                streak += 1
                expected = expected - timedelta(days=1)
            elif d == today - timedelta(days=1) and streak == 0:
                streak += 1
                expected = d - timedelta(days=1)
            else:
                break

    # --- Chart data ---

    # Score trend: last 30 tests in chronological order
    trend_rows = db.execute(
        'SELECT ts.score, ts.total, ts.taken_at, d.name AS deck_name '
        'FROM test_sessions ts JOIN decks d ON ts.deck_id = d.id '
        'WHERE ts.user_id = %s ORDER BY ts.taken_at ASC LIMIT 30',
        (user.id,)
    ).fetchall()

    trend_labels = []
    trend_scores = []
    for tr in trend_rows:
        pct = round(tr['score'] / tr['total'] * 100) if tr['total'] > 0 else 0
        trend_labels.append(tr['taken_at'].strftime('%d/%m'))
        trend_scores.append(pct)

    # Per-deck performance: avg and best score %
    deck_perf_rows = db.execute(
        'SELECT d.name, '
        '  ROUND(AVG(ts.score::numeric / NULLIF(ts.total,0) * 100)) AS avg_pct, '
        '  ROUND(MAX(ts.score::numeric / NULLIF(ts.total,0) * 100)) AS best_pct, '
        '  COUNT(ts.id) AS test_count '
        'FROM decks d '
        'LEFT JOIN test_sessions ts ON ts.deck_id = d.id AND ts.user_id = %s '
        'WHERE d.user_id = %s '
        'GROUP BY d.id, d.name ORDER BY d.name',
        (user.id, user.id)
    ).fetchall()

    deck_labels = []
    deck_avg = []
    deck_best = []
    for dr in deck_perf_rows:
        if dr['test_count'] and int(dr['test_count']) > 0:
            deck_labels.append(dr['name'])
            deck_avg.append(float(dr['avg_pct'] or 0))
            deck_best.append(float(dr['best_pct'] or 0))

    chart_data = json.dumps({
        'trend': {'labels': trend_labels, 'scores': trend_scores},
        'decks': {'labels': deck_labels, 'avg': deck_avg, 'best': deck_best}
    })

    return render_template(
        'dashboard/index.html',
        total_cards=total_cards,
        total_decks=total_decks,
        history=history,
        streak=streak,
        user=user,
        chart_data=chart_data,
        has_trend=len(trend_labels) > 0,
        has_deck_chart=len(deck_labels) > 0
    )
