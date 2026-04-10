import os
from flask_mail import Mail, Message

mail = Mail()


def send_verification_email(app, to_email, username, token):
    """
    Send an email-verification link to the new user.
    If MAIL_SERVER is not configured, the link is printed to the console
    so development works without any SMTP setup.
    """
    base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
    verify_url = f'{base_url}/auth/verify/{token}'

    if not os.environ.get('MAIL_SERVER'):
        # ── Development fallback ─────────────────────────────────────
        print('\n' + '=' * 60)
        print(f'  [DEV] Email verification for: {username} <{to_email}>')
        print(f'  Verification link:')
        print(f'  {verify_url}')
        print('=' * 60 + '\n')
        return

    # ── Production: send real email ──────────────────────────────────
    sender = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@linguaflip.com')

    msg = Message(
        subject='Verify your LinguaFlip account',
        sender=sender,
        recipients=[to_email]
    )

    msg.body = (
        f'Hello {username},\n\n'
        f'Thank you for registering at LinguaFlip!\n\n'
        f'Please verify your email by visiting:\n{verify_url}\n\n'
        f'If you did not create an account, ignore this email.\n\n'
        f'— The LinguaFlip Team'
    )

    msg.html = f'''
<!DOCTYPE html>
<html>
<body style="font-family:sans-serif;background:#f9fafb;padding:32px;">
  <div style="max-width:480px;margin:0 auto;background:#fff;border-radius:12px;
              padding:36px;border:1px solid #e5e7eb;">
    <h2 style="color:#2791F5;margin-top:0;">Welcome to LinguaFlip!</h2>
    <p>Hello <strong>{username}</strong>,</p>
    <p>Thank you for signing up. Click the button below to verify your email address
       and activate your account.</p>
    <div style="text-align:center;margin:32px 0;">
      <a href="{verify_url}"
         style="background:#F6B968;color:#1f2937;padding:14px 32px;
                text-decoration:none;border-radius:8px;font-weight:700;
                font-size:1rem;display:inline-block;">
        Verify My Email
      </a>
    </div>
    <p style="font-size:0.85rem;color:#6b7280;">
      Or paste this link in your browser:<br>
      <a href="{verify_url}" style="color:#2791F5;">{verify_url}</a>
    </p>
    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
    <p style="font-size:0.8rem;color:#9ca3af;">
      If you did not create a LinguaFlip account, please ignore this email.
    </p>
  </div>
</body>
</html>
'''

    with app.app_context():
        mail.send(msg)
