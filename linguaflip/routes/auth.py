from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from languages import LANGUAGES
from models.user import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        if not username_or_email or not password:
            flash('Please provide both username/email and password.', 'error')
            return render_template('auth/login.html')
        user = User.authenticate(username_or_email, password)
        if user is None:
            flash('Invalid username/email or password.', 'error')
            return render_template('auth/login.html')
        session.clear()
        session['user_id'] = int(user.id)
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('decks.index'))
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username    = request.form.get('username', '').strip()
        email       = request.form.get('email', '').strip()
        password    = request.form.get('password', '')
        confirm_pw  = request.form.get('confirm_password', '')
        native_lang = request.form.get('native_lang', 'en').strip()

        errors = []
        if not username:
            errors.append('Username is required.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_pw:
            errors.append('Passwords do not match.')
        if native_lang not in LANGUAGES:
            errors.append('Please select a valid native language.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('auth/register.html', languages=LANGUAGES)

        try:
            User.register(username, email, password, native_lang)
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            msg = str(e)
            if 'UNIQUE' in msg and 'username' in msg:
                flash('Username already taken.', 'error')
            elif 'UNIQUE' in msg and 'email' in msg:
                flash('Email already registered.', 'error')
            else:
                flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html', languages=LANGUAGES)

    return render_template('auth/register.html', languages=LANGUAGES)


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
