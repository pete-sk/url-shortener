from flask import Blueprint, render_template, url_for, redirect, abort, flash, request
from flask_login import current_user, login_required

from app import db
from app.models import Link
from app.main.forms import ShortenURL
from app.main.utils import generate_link

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ShortenURL()
    if form.validate_on_submit():
        original_url = form.original_url.data

        link = form.custom_link.data
        if not link:
            link = generate_link()
        if current_user.is_authenticated:
            user = current_user
        else:
            user = None
        new_entry = Link(link=link, original_url=original_url, user=user)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('main.index', shortened=link))

    shortened = Link.query.filter_by(link=request.args.get('shortened')).first()

    managed_links = []
    if current_user.is_authenticated:
        for entry in current_user.managed_links.order_by('id'):
            managed_links.append(entry)
    else:
        if shortened:
            managed_links.append(shortened)
    managed_links.reverse()

    return render_template('main/index.html', form=form, managed_links=managed_links)


@main.route('/<link>')
def unshorten(link):
    link = Link.query.filter_by(link=link).first()
    if link:
        db.session.commit()
        original_url = link.original_url
        if original_url.startswith(('http://', 'https://')):
            return redirect(original_url)
        else:
            return redirect('https://' + original_url)
    else:
        return abort(404)


@main.route('/delete/<link>', methods=['GET'])
@login_required
def delete_link(link):
    entry = Link.query.filter_by(link=link).first()
    if entry:
        if entry.user_id != current_user.id:
            abort(403)
        db.session.delete(entry)
        db.session.commit()
        flash('Entry has been deleted.')
    else:
        abort(404)

    return redirect(url_for('main.index'))
