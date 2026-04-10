import os
from flask import Blueprint, request, session, flash, redirect, url_for, g, jsonify
from functools import wraps
from models.deck import Deck
from models.flashcard import Flashcard
from services.ai_service import AIService

ai_bp = Blueprint('ai_bp', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@ai_bp.route('/suggest/<int:deck_id>', methods=['POST'])
@login_required
def suggest(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        return jsonify({'error': 'Deck not found'}), 404

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'AI features are not configured. Please set GEMINI_API_KEY.'}), 503

    service = AIService(api_key=api_key)
    if not service.check_rate_limit(user):
        return jsonify({'error': 'Rate limit exceeded. You can make at most 10 AI requests per 24 hours.'}), 429

    suggestions = service.generate_suggestions(deck)
    service.log_usage(user.id)

    return jsonify({'suggestions': suggestions})


@ai_bp.route('/add/<int:deck_id>', methods=['POST'])
@login_required
def add(deck_id):
    user = g.current_user
    deck = Deck.get_by_id(deck_id, user_id=user.id)
    if deck is None:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.get_json()
    if not data or 'cards' not in data:
        return jsonify({'error': 'Invalid request body'}), 400

    added = 0
    for item in data['cards']:
        front = item.get('front', '').strip()
        back = item.get('back', '').strip()
        if front and back:
            Flashcard.create(deck_id, front, back)
            added += 1

    return jsonify({'success': True, 'added': added})
