#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import literal, func, desc
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False, server_default="false")
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', back_populates="venue", cascade="all, delete-orphan")

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', back_populates="artist")

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'

  venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column('start_time', db.DateTime)
  venue = db.relationship("Venue", back_populates="shows")
  artist = db.relationship("Artist", back_populates="shows")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  city_state_key = {}
  upcoming_shows_count = 0
  venues = Venue.query.order_by('id').all()
  for venue in venues:
    venue_dict = {}
    venue_dict['id'] = venue.id
    venue_dict['name'] = venue.name
    for show in venue.shows:
      if show.start_time >= datetime.today():
        upcoming_shows_count +=1
    venue_dict['num_upcoming_shows'] = upcoming_shows_count
    key = f'{venue.city}|{venue.state}'
    if key in city_state_key:
      city_state_key[key].append(venue_dict)
    else:
      city_state_key[key] = [venue_dict]
 
  for key in city_state_key:
    city,state = key.split('|')
    city_venue = {}
    city_venue['city'] = city
    city_venue['state'] = state
    city_venue['venues'] = city_state_key[key]
    data.append(city_venue)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  data_array = []
  upcoming_shows_count = 0
  search_term = request.form['search_term']
  search_result = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()
  response['count'] = len(search_result)
  for venue in search_result: 
    venue_data = {}
    venue_data['id'] = venue.id
    venue_data['name'] = venue.name
    for show in venue.shows:
      if show.start_time >= datetime.today():
        upcoming_shows_count +=1
    venue_data['num_upcoming_shows'] = upcoming_shows_count
    data_array.append(venue_data)
  response['data'] = data_array

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  past_shows_count = 0
  upcoming_shows_count = 0
  past_shows_array = []
  upcoming_shows_array = []
  venue = Venue.query.get(venue_id)
  data['id'] = venue.id
  data['name'] = venue.name
  genres = venue.genres
  if genres.startswith('{') and genres.endswith('}'):
    genres = genres[1:-1]
  genres = genres.split(",")
  data['genres'] = genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  if venue.seeking_talent:
    data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  for show in venue.shows:
    artist = show.artist
    if show.start_time >= datetime.today():
      upcoming_shows_dict = {}
      upcoming_shows_count +=1
      upcoming_shows_dict['artist_id'] = artist.id
      upcoming_shows_dict['artist_name'] = artist.name
      upcoming_shows_dict['artist_image_link'] = artist.image_link
      upcoming_shows_dict['start_time'] = str(show.start_time)
      upcoming_shows_array.append(upcoming_shows_dict)
    else:
      past_shows_dict = {}
      past_shows_count +=1
      past_shows_dict['artist_id'] = artist.id
      past_shows_dict['artist_name'] = artist.name
      past_shows_dict['artist_image_link'] = artist.image_link
      past_shows_dict['start_time'] = str(show.start_time)
      past_shows_array.append(past_shows_dict)

  data['upcoming_shows_count'] = upcoming_shows_count
  data['past_shows_count'] = past_shows_count
  data['past_shows'] = past_shows_array
  data['upcoming_shows'] = upcoming_shows_array

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    form = VenueForm()
    if not form.validate():
      flash( form.errors )
      return render_template('forms/new_venue.html', form=form)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    address = request.form['address']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = True if request.form['seeking_talent'] == "True" else False
    seeking_description = request.form['seeking_description']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, website=website, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    return jsonify({'success':0})
  else:
    return jsonify({'success':1})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.order_by('id').all()
  for artist in artists:
    artist_data = {}
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  data_array = []
  upcoming_shows_count = 0
  search_term = request.form['search_term']
  search_result = Artist.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()
  response['count'] = len(search_result)
  for artist in search_result: 
    artist_data = {}
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    for show in artist.shows:
      if show.start_time >= datetime.today():
        upcoming_shows_count +=1
    artist_data['num_upcoming_shows'] = upcoming_shows_count
    data_array.append(artist_data)
  response['data'] = data_array
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  past_shows_count = 0
  upcoming_shows_count = 0
  past_shows_array = []
  upcoming_shows_array = []
  artist = Artist.query.get(artist_id)
  data['id'] = artist.id
  data['name'] = artist.name
  genres = artist.genres
  if genres.startswith('{') and genres.endswith('}'):
    genres = genres[1:-1]
  genres = genres.split(",")
  data['genres'] = genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  if artist.seeking_venue:
    data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  for show in artist.shows:
    venue = show.venue
    if show.start_time >= datetime.today():
      upcoming_shows_dict = {}
      upcoming_shows_count +=1
      upcoming_shows_dict['venue_id'] = venue.id
      upcoming_shows_dict['venue_name'] = venue.name
      upcoming_shows_dict['venue_image_link'] = venue.image_link
      upcoming_shows_dict['start_time'] = str(show.start_time)
      upcoming_shows_array.append(upcoming_shows_dict)
    else:
      past_shows_dict = {}
      past_shows_count +=1
      past_shows_dict['venue_id'] = venue.id
      past_shows_dict['venue_name'] = venue.name
      past_shows_dict['venue_image_link'] = venue.image_link
      past_shows_dict['start_time'] = str(show.start_time)
      past_shows_array.append(past_shows_dict)

  data['upcoming_shows_count'] = upcoming_shows_count
  data['past_shows_count'] = past_shows_count
  data['past_shows'] = past_shows_array
  data['upcoming_shows'] = upcoming_shows_array

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = {}
  artist_data = Artist.query.get(artist_id)
  artist['id'] = artist_id
  artist['name'] = artist_data.name
  artist['city'] = artist_data.city
  artist['state'] = artist_data.state
  artist['phone'] = artist_data.phone
  artist['image_link'] = artist_data.image_link
  artist['genres'] = artist_data.genres
  artist['website'] = artist_data.website
  artist['facebook_link'] = artist_data.facebook_link
  artist['seeking_venue'] = artist_data.seeking_venue
  artist['seeking_description'] = artist_data.seeking_description
  form.state.data = artist_data.state
  form.genres.data = artist_data.genres
  form.seeking_venue.data = str(artist_data.seeking_venue)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    form = ArtistForm()
    if not form.validate():
      flash( form.errors )
      return redirect(url_for('edit_artist', artist_id=artist_id))
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if request.form['seeking_venue'] == "True" else False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('There was en error while editing the artist!')
  else:
    flash('Artist edited succesfully.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = {}
  venue_data = Venue.query.get(venue_id)
  venue['id'] = venue_id
  venue['name'] = venue_data.name
  venue['city'] = venue_data.city
  venue['state'] = venue_data.state
  venue['phone'] = venue_data.phone
  venue['image_link'] = venue_data.image_link
  venue['address'] = venue_data.address
  venue['genres'] = venue_data.genres
  venue['website'] = venue_data.website
  venue['facebook_link'] = venue_data.facebook_link
  venue['seeking_talent'] = venue_data.seeking_talent
  venue['seeking_description'] = venue_data.seeking_description
  form.state.data = venue_data.state
  form.genres.data = venue_data.genres
  form.seeking_talent.data = str(venue_data.seeking_talent)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    form = VenueForm()
    if not form.validate():
      flash( form.errors )
      return redirect(url_for('edit_venue', venue_id=venue_id))
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = True if request.form['seeking_talent'] == "True" else False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('There was en error while editing the venue!')
  else:
    flash('Venue edited succesfully.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    form = ArtistForm()
    if not form.validate():
      flash( form.errors )
      return render_template('forms/new_artist.html', form=form)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = True if request.form['seeking_venue'] == "True" else False
    seeking_description = request.form['seeking_description']
    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, website=website, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.order_by(desc('start_time')).all()
  for show in shows:
    show_data = {}
    venue = show.venue
    artist = show.artist
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = venue.name
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = artist.name
    show_data['artist_image_link'] = artist.image_link
    show_data['start_time'] = str(show.start_time)
    data.append(show_data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows(): 
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
