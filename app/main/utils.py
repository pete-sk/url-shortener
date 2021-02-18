import requests
from user_agents import parse
from random import randint

from app import db
from app.models import Link


def generate_link(length=6, lower=True, upper=True, numbers=True):
    # ambiguous characters excluded
    lowchars = 'qwertyupadfghjkxcvnm'
    upchars = 'QWERTYUPAFGHKLXCVNM'
    nums = '23456789'

    scope = ''
    if lower:
        scope += lowchars
    if upper:
        scope += upchars
    if numbers:
        scope += nums

    link = ''
    if not scope:
        pass
    else:
        for i in range(length):
            link += scope[randint(0, len(scope)-1)]

    taken = Link.query.filter_by(link=link).first()
    if taken:
        link = generate_link()

    return link


def delete_link_and_stats(link):
    for click in link.clicks:
        db.session.delete(click)
    db.session.delete(link)
    db.session.commit()


def parse_clicks(clicks):
    class ParsedClick:
        def __init__(self, date_clicked, ip_address, location, os, browser, referrer):
            self.date_clicked = date_clicked
            self.ip_address = ip_address
            self.location = location
            self.os = os
            self.browser = browser
            self.referrer = referrer

    parsed_clicks = []
    for click in clicks:
        date_clicked = click.date_clicked
        ip_address = click.ip_address

        api_key = ''
        ipstack = requests.get(f'http://api.ipstack.com/{ip_address}?access_key={api_key}').json()
        location = ipstack["country_name"] if ipstack["country_name"] else 'Unknown'

        user_agent = parse(click.user_agent)
        os = user_agent.os.family
        browser = user_agent.browser.family
        referrer = click.referrer_page

        parsed_clicks.append(ParsedClick(date_clicked, ip_address, location, os, browser, referrer))

    return parsed_clicks
