from random import randint

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
