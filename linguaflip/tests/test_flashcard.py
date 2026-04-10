"""Unit tests for the Flashcard model."""
import pytest
from models.user import User
from models.deck import Deck
from models.flashcard import Flashcard


@pytest.fixture()
def deck(app_ctx):
    user = User.register('carduser', 'carduser@example.com', 'password', 'en')
    return Deck.create(user.id, 'Test Deck', 'en', 'es')


def test_create_flashcard(deck, app_ctx):
    card = Flashcard.create(deck.id, 'hello', 'hola')
    assert card is not None
    assert card.id is not None
    assert card.front == 'hello'
    assert card.back == 'hola'
    assert card.deck_id == deck.id


def test_get_by_id(deck, app_ctx):
    card = Flashcard.create(deck.id, 'cat', 'gato')
    fetched = Flashcard.get_by_id(card.id)
    assert fetched is not None
    assert fetched.front == 'cat'
    assert fetched.back == 'gato'


def test_get_by_id_missing(app_ctx):
    card = Flashcard.get_by_id(999999)
    assert card is None


def test_update_flashcard(deck, app_ctx):
    card = Flashcard.create(deck.id, 'dog', 'perro')
    card.update('dog (animal)', 'perro (animal)')
    assert card.front == 'dog (animal)'
    assert card.back == 'perro (animal)'
    fetched = Flashcard.get_by_id(card.id)
    assert fetched.front == 'dog (animal)'
    assert fetched.back == 'perro (animal)'


def test_delete_flashcard(deck, app_ctx):
    card = Flashcard.create(deck.id, 'water', 'agua')
    card_id = card.id
    card.delete()
    assert Flashcard.get_by_id(card_id) is None


def test_deck_get_cards(deck, app_ctx):
    Flashcard.create(deck.id, 'one', 'uno')
    Flashcard.create(deck.id, 'two', 'dos')
    Flashcard.create(deck.id, 'three', 'tres')
    cards = deck.get_cards()
    assert len(cards) == 3
    fronts = {c.front for c in cards}
    assert fronts == {'one', 'two', 'three'}


def test_deck_stats_with_cards(deck, app_ctx):
    Flashcard.create(deck.id, 'a', 'b')
    Flashcard.create(deck.id, 'c', 'd')
    stats = deck.get_stats()
    assert stats['card_count'] == 2
    assert stats['test_count'] == 0
