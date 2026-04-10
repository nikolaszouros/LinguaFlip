"""Unit tests for the User model."""
import pytest
from models.user import User


def test_register_creates_user(app_ctx):
    user = User.register('alice', 'alice@example.com', 'password123', 'en')
    assert user is not None
    assert user.id is not None
    assert user.username == 'alice'
    assert user.email == 'alice@example.com'
    assert user.native_lang == 'en'


def test_register_hashes_password(app_ctx):
    user = User.register('bob', 'bob@example.com', 'supersecret', 'fr')
    # The stored hash should not equal the plain-text password
    assert user.password_hash != 'supersecret'
    assert len(user.password_hash) > 20


def test_authenticate_correct_password(app_ctx):
    User.register('charlie', 'charlie@example.com', 'correct_pass', 'de')
    user = User.authenticate('charlie', 'correct_pass')
    assert user is not None
    assert user.username == 'charlie'


def test_authenticate_with_email(app_ctx):
    User.register('diana', 'diana@example.com', 'mypassword', 'es')
    user = User.authenticate('diana@example.com', 'mypassword')
    assert user is not None
    assert user.username == 'diana'


def test_authenticate_wrong_password(app_ctx):
    User.register('eve', 'eve@example.com', 'realpassword', 'it')
    user = User.authenticate('eve', 'wrongpassword')
    assert user is None


def test_authenticate_unknown_user(app_ctx):
    user = User.authenticate('nobody', 'anything')
    assert user is None


def test_get_by_id(app_ctx):
    created = User.register('frank', 'frank@example.com', 'pass1234', 'en')
    fetched = User.get_by_id(created.id)
    assert fetched is not None
    assert fetched.username == 'frank'


def test_get_by_id_missing(app_ctx):
    user = User.get_by_id(999999)
    assert user is None


def test_ai_usage_today_starts_zero(app_ctx):
    user = User.register('grace', 'grace@example.com', 'pass', 'en')
    assert user.get_ai_usage_today() == 0
