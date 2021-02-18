from datetime import datetime
from collections import Counter
from flask import Blueprint, render_template, url_for, redirect, abort, flash, request, jsonify
from flask_login import current_user, login_required

from app import db
from app.models import Link, Click
from app.main.forms import ShortenURL
from app.main.utils import generate_link, delete_link_and_stats, parse_clicks

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
        # save click info
        ip_address = request.access_route[-1]
        user_agent = request.user_agent.string
        referrer_page = request.referrer if request.referrer else 'None'
        click_info = Click(link_id=link.id, ip_address=ip_address, user_agent=user_agent, referrer_page=referrer_page)
        db.session.add(click_info)
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
        delete_link_and_stats(entry)
        flash('Entry has been deleted.')
    else:
        abort(404)

    return redirect(url_for('main.index'))


@main.route('/analytics/<link>')
@login_required
def analytics(link):
    entry = Link.query.filter_by(link=link).first()
    if entry:
        if entry.user_id != current_user.id:
            abort(403)
    else:
        abort(404)

    time_format = "%A, %Y-%m-%d, %H:%M:%S UTC"
    date_created = entry.date_created.strftime(time_format)

    clicks = parse_clicks(entry.clicks)
    num_of_clicks = len(clicks)

    if not num_of_clicks:
        return render_template('main/analytics.html', entry=entry, date_created=date_created,
                               num_of_clicks=num_of_clicks)

    clicks_today = sum(c.date_clicked.date() == datetime.today().date() for c in clicks)
    last_click = clicks[-1].date_clicked.strftime(time_format)
    first_click = clicks[0].date_clicked.strftime(time_format)

    top_locations = Counter(c.location for c in clicks).most_common()
    if len(top_locations) > 10:
        top_locations = top_locations[:10]
        remaining_locations = num_of_clicks - sum(location[1] for location in top_locations)
        top_locations.append(('Other', remaining_locations))

    top_platforms = Counter(c.os for c in clicks).most_common()
    if len(top_platforms) > 10:
        top_platforms = top_platforms[:10]
        remaining_platforms = num_of_clicks - sum(platform[1] for platform in top_platforms)
        top_platforms.append(('Other', remaining_platforms))

    top_browsers = Counter(c.browser for c in clicks).most_common()
    if len(top_browsers) > 10:
        top_browsers = top_browsers[:10]
        remaining_browsers = num_of_clicks - sum(browser[1] for browser in top_browsers)
        top_browsers.append(('Other', remaining_browsers))

    top_referrers = Counter(c.referrer for c in clicks).most_common()
    if len(top_referrers) > 10:
        top_referrers = top_referrers[:10]
        remaining_referrers = num_of_clicks - sum(referrer[1] for referrer in top_referrers)
        top_referrers.append(('Other', remaining_referrers))

    return render_template('main/analytics.html', entry=entry, date_created=date_created, num_of_clicks=num_of_clicks,
                           clicks_today=clicks_today, last_click=last_click, first_click=first_click,
                           top_locations=top_locations, top_platforms=top_platforms, top_browsers=top_browsers,
                           top_referrers=top_referrers)


@main.route('/statistics/<link>')
@login_required
def statistics(link):
    entry = Link.query.filter_by(link=link).first()
    if entry:
        if entry.user_id != current_user.id:
            abort(403)
    else:
        abort(404)

    time_format = "%A, %Y-%m-%d, %H:%M:%S UTC"

    page = request.args.get('page', 1, type=int)
    clicks = parse_clicks(entry.clicks.order_by(Click.click_id.desc())
                          .paginate(page=page, per_page=10, error_out=False).items)
    clicks_dict = []
    for click in clicks:
        clicks_dict.append({'date_clicked': click.date_clicked.strftime(time_format), 'ip_address': click.ip_address,
                            'location': click.location, 'os': click.os, 'browser': click.browser,
                            'referrer': click.referrer})

    return jsonify(clicks_dict)
