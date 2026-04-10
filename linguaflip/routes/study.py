import json
from flask import Blueprint, render_template, session, flash, redirect, url_for, g
from functools import wraps
from models.deck import Deck

study = Blueprint('study', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@study.route('/<int:deck_id>')
@login_required
def index(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    cards = deck.get_cards()
    if not cards:
        flash('This deck has no cards yet. Add some cards before studying.', 'error')
        return redirect(url_for('decks.detail', deck_id=deck_id))
    cards_json = json.dumps([{'id': c.id, 'front': c.front, 'back': c.back} for c in cards])
    return render_template('study/index.html', deck=deck, cards_json=cards_json, card_count=len(cards))
