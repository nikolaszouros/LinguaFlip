import json
import random
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, g, jsonify
from functools import wraps
from models.deck import Deck
from models.flashcard import Flashcard
from models.test_session import TestSession

test_bp = Blueprint('test_bp', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@test_bp.route('/<int:deck_id>')
@login_required
def index(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    cards = deck.get_cards()
    if not cards:
        flash('This deck has no cards yet. Add some cards before testing.', 'error')
        return redirect(url_for('decks.detail', deck_id=deck_id))
    shuffled = cards[:]
    random.shuffle(shuffled)
    cards_json = json.dumps([{'id': c.id, 'front': c.front, 'back': c.back} for c in shuffled])
    return render_template('test/index.html', deck=deck, cards_json=cards_json, card_count=len(cards))


@test_bp.route('/<int:deck_id>/submit', methods=['POST'])
@login_required
def submit(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({'error': 'Invalid request body'}), 400

    answers = data['answers']
    results = []
    score = 0

    for answer_item in answers:
        card_id = answer_item.get('card_id')
        given = answer_item.get('answer', '').strip()
        card = Flashcard.get_by_id(card_id)
        if card is None or card.deck_id != deck_id:
            continue
        expected = card.back.strip()
        correct = given.lower() == expected.lower()
        if correct:
            score += 1
        results.append({
            'card_id': card_id,
            'correct': correct,
            'expected': expected,
            'given': given
        })

    total = len(results)
    ts = TestSession.create(user.id, deck_id, total)
    ts.update_score(score)

    return jsonify({
        'score': score,
        'total': total,
        'session_id': ts.id,
        'results': results
    })
