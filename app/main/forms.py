from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, ValidationError, regexp

from app.models import Link


url_regex = r'(https?:\/\/)?([\w\-])+\.{1}([a-zA-Z]{2,63})([\/\w-]*)*\/?\??([^#\n\r]*)?#?([^\n\r]*)'
custom_link_regex = r'(^[a-zA-Z0-9-]*$)'


class ShortenURL(FlaskForm):
    original_url = StringField('Enter URL', validators=[Length(min=1, max=9999), DataRequired(),
                                                        regexp(url_regex, message='Invalid URL.')])
    custom_link = StringField('Custom alias (optional)', validators=[regexp(custom_link_regex,
                                                                            message='You can only enter letters, '
                                                                                    'numbers and dashes.')])
    submit = SubmitField('Shorten URL')

    def validate_custom_link(self, custom_link):
        link = Link.query.filter_by(link=custom_link.data).first()
        if link:
            raise ValidationError('Custom link already taken.')

        length = len(custom_link.data)
        if length != 0:
            if length < 3 or length > 16:
                raise ValidationError('Field must be between 3 and 16 characters long.')
