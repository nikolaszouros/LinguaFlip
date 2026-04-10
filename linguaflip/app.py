import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, url_for, session, g
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

    # ── Blueprints ────────────────────────────────────────────────────
    from routes.auth import auth
    from routes.decks import decks
    from routes.cards import cards
    from routes.study import study
    from routes.test import test_bp
    from routes.ai import ai_bp
    from routes.profile import profile

    app.register_blueprint(auth,    url_prefix='/auth')
    app.register_blueprint(decks,   url_prefix='/decks')
    app.register_blueprint(cards,   url_prefix='/cards')
    app.register_blueprint(study,   url_prefix='/study')
    app.register_blueprint(test_bp, url_prefix='/test')
    app.register_blueprint(ai_bp,   url_prefix='/ai')
    app.register_blueprint(profile, url_prefix='/profile')

    # ── Root route ────────────────────────────────────────────────────
    @app.route('/')
    def index():
        from models.deck import Deck
        user_decks = []
        if g.get('current_user'):
            user_decks = Deck.get_all_for_user(g.current_user.id)
        return render_template('index.html', user_decks=user_decks)

    # ── Template filter: format datetime as dd/mm/yyyy hh:mm ─────────
    @app.template_filter('fmt_dt')
    def format_datetime(value):
        if value is None:
            return '—'
        try:
            return value.strftime('%d/%m/%Y %H:%M')
        except AttributeError:
            return str(value)

    # ── Current user injection ────────────────────────────────────────
    @app.before_request
    def load_current_user():
        from models.user import User
        user_id = session.get('user_id')
        if user_id is not None:
            g.current_user = User.get_by_id(user_id)
            if g.current_user is None:
                session.clear()
        else:
            g.current_user = None

    @app.context_processor
    def inject_current_user():
        return {'current_user': g.get('current_user', None)}

    # ── Database ──────────────────────────────────────────────────────
    from db.database import init_db, close_db

    with app.app_context():
        try:
            init_db()
        except Exception as e:
            raise RuntimeError(
                f"\n\n  Could not connect to the database.\n"
                f"  Make sure the database exists in PostgreSQL and\n"
                f"  your DATABASE_URL in .env is correct.\n\n"
                f"  Original error: {e}\n"
            ) from None

    app.teardown_appcontext(close_db)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
