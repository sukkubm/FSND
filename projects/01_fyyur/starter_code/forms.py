from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, RadioField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL
from enums import State, Genre
from wtforms.validators import ValidationError

def anyof_genres(values):
  error_message = 'Invalid value, must be one of: {0}.'.format( ','.join(values) )
  def _validate(form, field):
    error = False
    for value in field.data:
      if value not in values:
        error = True
    if error:
      raise ValidationError(error_message)
  return _validate

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), anyof_genres( [ (choice.value) for choice in Genre ] )],
        choices=Genre.choices()
    )
    website = StringField(
        'website', validators=[URL(message=('Please enter a valid website URL.'))]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message=('Please enter a valid facebook URL Link.'))]
    )
    seeking_talent = RadioField(
        'seeking_talent', default='False', choices=[('True','Yes'),('False','No')]
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
    )
    website = StringField(
        'website', validators=[URL(message=('Please enter a valid website URL.'))]
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL(message=('Please enter a valid facebook URL Link.'))]
    )
    seeking_venue = RadioField(
        'seeking_venue', default='False', choices=[('True','Yes'),('False','No')]
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM