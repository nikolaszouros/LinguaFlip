"""Unit tests for the Deck model."""
import pytest
from models.user import User
from models.deck import Deck


@pytest.fixture()
def user(app_ctx):
    return User.register('deckuser', 'deckuser@example.com', 'password', 'en')


def test_create_deck(user, app_ctx):
    deck = Deck.create(user.id, 'My Spanish Deck', 'en', 'es')
    assert deck is not None
    assert deck.id is not None
    assert deck.name == 'My Spanish Deck'
    assert deck.source_lang == 'en'
    assert deck.target_lang == 'es'
    assert deck.user_id == user.id


def test_get_by_id(user, app_ctx):
    deck = Deck.create(user.id, 'French Words', 'en', 'fr')
    fetched = Deck.get_by_id(deck.id)
    assert fetched is not None
    assert fetched.name == 'French Words'


def test_get_by_id_with_user_id(user, app_ctx):
    deck = Deck.create(user.id, 'German Deck', 'en', 'de')
    # Correct owner
    fetched = Deck.get_by_id(deck.id, user_id=user.id)
    assert fetched is not None
    # Wrong owner
    wrong = Deck.get_by_id(deck.id, user_id=user.id + 999)
    assert wrong is None


def test_get_all_for_user(user, app_ctx):
    Deck.create(user.id, 'Deck A', 'en', 'es')
    Deck.create(user.id, 'Deck B', 'en', 'fr')
    decks = Deck.get_all_for_user(user.id)
    assert len(decks) == 2
    names = {d.name for d in decks}
    assert 'Deck A' in names
    assert 'Deck B' in names


def test_update_deck(user, app_ctx):
    deck = Deck.create(user.id, 'Old Name', 'en', 'es')
    deck.update('New Name')
    fetched = Deck.get_by_id(deck.id)
    assert fetched.name == 'New Name'


def test_delete_deck(user, app_ctx):
    deck = Deck.create(user.id, 'Temp Deck', 'en', 'es')
    deck_id = deck.id
    deck.delete()
    assert Deck.get_by_id(deck_id) is None


def test_get_stats_empty(user, app_ctx):
    deck = Deck.create(user.id, 'Empty Deck', 'en', 'es')
    stats = deck.get_stats()
    assert stats['card_count'] == 0
    assert stats['test_count'] == 0
    assert stats['best_score'] is None
    assert stats['last_score'] is None


def test_get_cards_empty(user, app_ctx):
    deck = Deck.create(user.id, 'Card Deck', 'en', 'fr')
    cards = deck.get_cards()
    assert cards == []
