from smtplib import SMTPRecipientsRefused
from flask import Blueprint, Markup, render_template, request, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required

from app import db, bcrypt
from app.models import User
from app.account.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm,
                               PasswordPrompt)
from app.account.utils import send_activation_email, send_reset_email, wipe_user_data

account = Blueprint('account', __name__)


@account.route('/account/register', methods=['GET', 'POST'])
def register():
    title = 'Create an account'

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=email, password=hashed_password)

        try:
            send_activation_email(user)
            flash('Account created! Verification link has been sent to your email.')
        except SMTPRecipientsRefused:
            flash('Entered email address is invalid!')
            return redirect(url_for('account.register'))
        except:
            user.activated = True
            flash('Account created! You can now log in.')

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('account.login'))

    return render_template('account/register.html', title=title, form=form)


@account.route('/account/activate-account/resend-activation-link/<string:email>')
def resend_activation_link(email):
    user = User.query.filter_by(email=email).first()
    if user:
        send_activation_email(user)
        flash('Verification link has been sent to your email.')
    else:
        flash('Something went wrong. Try again.')
    return redirect(url_for('account.login'))


@account.route('/account/activate-account/<token>')
def activate_account_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    verify = User.verify_activation_token(token)
    user = verify[0]
    email = verify[1]
    if not user or email != user.email:
        flash('Invalid or expired token.')
        return redirect(url_for('account.login'))
    user.activated = True
    db.session.commit()
    flash('Your email has been confirmed. You can now log in.')
    return redirect(url_for('account.login'))


@account.route('/account/login', methods=['GET', 'POST'])
def login():
    title = 'Login'

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.activated != 0:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash(Markup(f'Your email address is not confirmed. Check your email for the verification link or '
                      f'<a href="{url_for("account.resend_activation_link", email=user.email)}">'
                             f'send again.</a>'))
        else:
            flash('Invalid email or password!')

    return render_template('account/login.html', title=title, form=form)


@account.route('/account/logout')
def logout():
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('main.index'))


@account.route('/account/settings/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    title = 'Delete Account'

    form = PasswordPrompt()
    if form.validate_on_submit():
        password = form.password.data
        if bcrypt.check_password_hash(current_user.password, password):
            wipe_user_data(current_user)
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted.')
            return redirect(url_for('main.index'))
        else:
            flash('The password you entered is incorrect.')
            return redirect(url_for('account.delete_account'))

    return render_template('account/delete_account.html', title=title, form=form)


@account.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    title = 'Account Settings'

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            if form.email.data != current_user.email:
                current_user.email = form.email.data
                current_user.activated = False
                send_activation_email(current_user)
                flash('Email address has been changed. Please check your email for the verification link.')
            if form.new_password.data:
                current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                flash('Password has been updated.')
            db.session.commit()
            return redirect(url_for('account.account_settings'))
    elif request.method == 'GET':
        form.email.data = current_user.email

    return render_template('account/account_settings.html', title=title, form=form)


@account.route('/account/reset-password', methods=['GET', 'POST'])
def reset_request():
    title = 'Reset Password'

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
            flash('An email with the reset link has been sent.')
        except:
            flash('Cannot send a reset link at the moment. Please try again later.')
        return redirect(url_for('account.login'))
    return render_template('account/password_reset_request.html', title=title, form=form)


@account.route('/account/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    title = 'Reset Password'

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('account.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(user.password, form.password.data):
            flash('The password you entered is already set.')
            return redirect(url_for('account.reset_token', token=token))
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Password has been updated.')
        return redirect(url_for('account.login'))

    return render_template('account/password_reset_token.html', title=title, form=form)
