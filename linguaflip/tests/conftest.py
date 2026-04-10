"""
Shared pytest fixtures for LinguaFlip tests.

Each test gets its own Flask application context backed by a fresh
in-memory SQLite database, so tests are fully isolated.
"""
import sys
import os

# Ensure the linguaflip package root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Point all tests at an in-memory SQLite database before any app import
os.environ['DATABASE_PATH'] = ':memory:'
os.environ['SECRET_KEY'] = 'test-secret'

import pytest
from app import create_app


@pytest.fixture()
def app():
    """Create a Flask app configured for testing."""
    test_app = create_app()
    test_app.config['TESTING'] = True
    return test_app


@pytest.fixture()
def app_ctx(app):
    """
    Push a fresh application context for the duration of a single test.

    Because DATABASE_PATH is ':memory:', each new connection (i.e. each new
    app context) starts with an empty database, so we re-run init_db() here.
    """
    ctx = app.app_context()
    ctx.push()
    from db.database import init_db
    init_db()
    yield
    ctx.pop()
