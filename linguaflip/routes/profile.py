from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app
from functools import wraps
import os
from werkzeug.utils import secure_filename
from languages import LANGUAGES
from db.database import get_db
from models.deck import Deck

profile = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or g.current_user is None:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@profile.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user = g.current_user
    db = get_db()

    if request.method == 'POST':
        action = request.form.get('action', '')

        # --- Profile picture upload ---
        if 'profile_pic' in request.files and request.files['profile_pic'].filename:
            file = request.files['profile_pic']
            if not allowed_file(file.filename):
                flash('Please upload a valid image (JPG, PNG, or WebP).', 'error')
            else:
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f'user_{user.id}.{ext}'
                uploads_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
                os.makedirs(uploads_dir, exist_ok=True)
                file.save(os.path.join(uploads_dir, filename))
                db.execute('UPDATE users SET profile_pic = %s WHERE id = %s', (filename, user.id))
                db.commit()
                flash('Profile picture updated.', 'success')
            return redirect(url_for('profile.index'))

        # --- Username change ---
        if action == 'change_username':
            new_username = request.form.get('new_username', '').strip()
            if not new_username:
                flash('Username cannot be empty.', 'error')
            elif len(new_username) < 3:
                flash('Username must be at least 3 characters.', 'error')
            elif new_username == user.username:
                flash('That is already your username.', 'error')
            else:
                try:
                    db.execute('UPDATE users SET username = %s WHERE id = %s',
                               (new_username, user.id))
                    db.commit()
                    flash('Username updated.', 'success')
                except Exception as e:
                    if 'unique' in str(e).lower() or 'UNIQUE' in str(e):
                        flash('Username already taken.', 'error')
                    else:
                        flash('Could not update username.', 'error')
            return redirect(url_for('profile.index'))

        # --- Native language update ---
        native_lang = request.form.get('native_lang', '').strip()
        if native_lang not in LANGUAGES:
            flash('Invalid language selected.', 'error')
        else:
            db.execute('UPDATE users SET native_lang = %s WHERE id = %s',
                       (native_lang, user.id))
            db.commit()
            flash('Profile updated.', 'success')
        return redirect(url_for('profile.index'))

    # Stats
    deck_list = Deck.get_all_for_user(user.id)

    card_row = db.execute(
        'SELECT COUNT(*) AS cnt FROM flashcards f '
        'JOIN decks d ON f.deck_id = d.id WHERE d.user_id = %s',
        (user.id,)
    ).fetchone()
    total_cards = card_row['cnt'] if card_row else 0

    test_row = db.execute(
        'SELECT COUNT(*) AS cnt FROM test_sessions WHERE user_id = %s',
        (user.id,)
    ).fetchone()
    total_tests = test_row['cnt'] if test_row else 0

    return render_template(
        'profile/index.html',
        user=user,
        languages=LANGUAGES,
        decks=deck_list,
        total_cards=total_cards,
        total_tests=total_tests,
    )
