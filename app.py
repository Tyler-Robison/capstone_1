from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models.user import db, connect_db, User
from models.search import Search
from forms import RegisterForm, LoginForm, SearchForm
import googlemaps
from secret import google_key
import requests
# from operator import attrgetter

gmaps = googlemaps.Client(key=google_key)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///weather_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "chickensrawesome"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404

@app.route('/')
def home_page():
    """Redirects to registration page 
    or search page if user already logged in"""

    if "user_id" in session:
        return redirect('/search')

    else:
        return redirect('/register')


@app.route('/register', methods=["POST", "GET"])
def register():
    """Allows user to register"""

    if "user_id" in session:
        flash('Already registered')
        return redirect('/search')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        is_admin = False
        # admin user can only be created through seed.py or in terminal

        try:
            new_user = User.register(
                username, password, first_name, last_name, email, is_admin)
            db.session.add(new_user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Registration failed, need unique username')
            return redirect('/register')

        session["user_id"] = new_user.id
        flash('Account Created!')

        return redirect(f'/users/{session["user_id"]}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Logs in a user"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        logged_user = User.authenticate(username, password)
        if logged_user:
            session['user_id'] = logged_user.id
            return redirect('/search')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Logs out a user"""

    session.pop('user_id')
    return redirect('/')


@app.route('/users/<int:user_id>')
def display_user_info(user_id):
    """Shows profile information"""

    user = User.query.get_or_404(user_id)

    return render_template('user_info.html', user=user)


# @app.route('/test', methods=["GET", "POST"])
# def search():
#     """Displays search form"""

#     form = SearchForm()

#     if form.validate_on_submit():
#         # try/except needed
#         coords = Search.get_coords(form.address.data)
#         weather = Search.get_weather(coords)
#         return render_template('test.html', form=form, weather=weather)

#     return render_template('test.html', form=form)


@app.route('/search', methods=["GET", "POST"])
def find_hikes():

    form = SearchForm()
    form.radius.choices = [(5000, 3), (8000, 5), (12500, 8), (16000, 10), (24000, 15), (32000, 20)]

    if form.validate_on_submit():
        address = form.address.data
        coords = Search.get_coords(address)
        radius = form.radius.data
        
        raw_results = Search.get_hikes(coords, radius)
        hikes = Search.show_search_results(raw_results)

        return render_template('search.html', form=form, hikes=hikes, address=address, coords=coords)

    return render_template('search.html', form=form)


@app.route('/search/details', methods=["POST"])
def return_search_details():
    """Receives request from front-end"""

    destination_id = request.json['destination_id']
    origin_address = request.json['origin_address']
    

    directions = Search.get_directions(origin_address, destination_id)


    return jsonify(directions)
    

# @app.route('/search/weather', methods=["POST"])   
# def return_weather():
#     """Receives coords and returns weather"""
#     coords_str = request.json['coords']
#     # "{'lat': 42.3292493, 'lng': -71.352353}"
#     # has to be converted from str to dict
#     coords = eval(coords_str)
#     weather = Search.get_weather(coords)


#     return jsonify(weather)

@app.route('/search/forecast', methods=["POST"])
def return_forecast():
    """Receives coords and returns 5-day forecast"""    

    coords_str = request.json['coords']
    coords = eval(coords_str)
    forecast = Search.get_forecast(coords)

    return jsonify(forecast)


