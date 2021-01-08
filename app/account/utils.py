from flask import url_for
from flask_mail import Message

from app import mail, db
from app.models import Link


def send_activation_email(user):
    token = user.get_activation_token()
    link = url_for('account.activate_account_token', token=token, _external=True)
    msg = Message('Verify your email', sender='noreply@shortenu.herokuapp.com', recipients=[user.email])
    msg.html = f'''<p>To verify your URL Shortener account email, visit the following link:<br><br>
<a href="{link}">{link}</a></p>'''
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    link = url_for('account.reset_token', token=token, _external=True)
    msg = Message('Password Reset Request', sender='noreply@shortenu.herokuapp.com', recipients=[user.email])
    msg.html = f'''<p>To reset your URL Shortener account password, visit the following link:<br><br>
<a href="{link}">{link}</a></p>'''
    mail.send(msg)


def wipe_user_data(user):
    managed_links = Link.query.filter_by(user_id=user.id).all()
    for entry in managed_links:
        db.session.delete(entry)
    db.session.commit()
