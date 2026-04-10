import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, jsonify
from functools import wraps
from models.deck import Deck
from models.flashcard import Flashcard
from services.ai_service import AIService

cards = Blueprint('cards', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@cards.route('/<int:deck_id>/new', methods=['GET', 'POST'])
@login_required
def new(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        flash('Deck not found.', 'error')
        return redirect(url_for('decks.index'))
    if request.method == 'POST':
        front = request.form.get('front', '').strip()
        back = request.form.get('back', '').strip()
        if not front or not back:
            flash('Both front and back text are required.', 'error')
            return render_template('cards/new.html', deck=deck)
        Flashcard.create(deck_id, front, back)
        flash('Card added!', 'success')
        if request.form.get('add_another'):
            return redirect(url_for('cards.new', deck_id=deck_id))
        return redirect(url_for('decks.detail', deck_id=deck_id))
    return render_template('cards/new.html', deck=deck)


@cards.route('/<int:deck_id>/translate', methods=['POST'])
@login_required
def translate(deck_id):
    deck = Deck.get_by_id(deck_id, user_id=g.current_user.id)
    if deck is None:
        return jsonify({'error': 'Deck not found'}), 404
    data = request.get_json()
    word = (data or {}).get('word', '').strip()
    if not word:
        return jsonify({'error': 'No word provided'}), 400
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'AI not configured'}), 503
    service = AIService(api_key=api_key)
    translation = service.translate(word, deck.source_lang, deck.target_lang)
    if translation is None:
        return jsonify({'error': 'Translation failed'}), 500
    return jsonify({'translation': translation})


@cards.route('/<int:card_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(card_id):
    user = g.current_user
    card = Flashcard.get_by_id(card_id)
    if card is None:
        flash('Card not found.', 'error')
        return redirect(url_for('decks.index'))
    deck = Deck.get_by_id(card.deck_id, user_id=user.id)
    if deck is None:
        flash('Access denied.', 'error')
        return redirect(url_for('decks.index'))
    if request.method == 'POST':
        front = request.form.get('front', '').strip()
        back = request.form.get('back', '').strip()
        if not front or not back:
            flash('Both front and back text are required.', 'error')
            return render_template('cards/edit.html', card=card, deck=deck)
        card.update(front, back)
        flash('Card updated.', 'success')
        return redirect(url_for('decks.detail', deck_id=deck.id))
    return render_template('cards/edit.html', card=card, deck=deck)


@cards.route('/<int:card_id>/delete', methods=['POST'])
@login_required
def delete(card_id):
    user = g.current_user
    card = Flashcard.get_by_id(card_id)
    if card is None:
        flash('Card not found.', 'error')
        return redirect(url_for('decks.index'))
    deck = Deck.get_by_id(card.deck_id, user_id=user.id)
    if deck is None:
        flash('Access denied.', 'error')
        return redirect(url_for('decks.index'))
    deck_id = card.deck_id
    card.delete()
    flash('Card deleted.', 'success')
    return redirect(url_for('decks.detail', deck_id=deck_id))
