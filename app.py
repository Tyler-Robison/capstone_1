from flask import Flask, request, render_template, redirect, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from user import db, connect_db, User
from search import Search
from forms import RegisterForm, LoginForm, SearchForm, UserEditForm, ChangePwdForm
import googlemaps
from secret import google_key
import requests
import os
# from operator import attrgetter

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///weather_app'))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///weather_app'
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


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# User Routes ##########################################

@app.route('/')
def home_page():
    """Redirects to registration page 
    or search page if user already logged in"""

    if g.user:
        flash('Welcome Back!')
        return redirect('/search')

    else:
        flash('Please Create Account')
        return redirect('/register')


@app.route('/register', methods=["POST", "GET"])
def register():
    """Allows user to register"""

    if g.user:
        # if "user_id" in session:
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
            flash('Username or email already taken')
            return redirect('/register')

        session[CURR_USER_KEY] = new_user.id
        flash('Account Created!')

        return redirect('/search')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Logs in a user"""

    if g.user:
        # if "user_id" in session:
        flash('Already logged in')
        return redirect('/search')

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        logged_user = User.authenticate(username, password)
        if logged_user:
            session[CURR_USER_KEY] = logged_user.id
            flash(f'Welcome back {logged_user.username}')
            return redirect('/search')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Logs out a user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    flash('Logout Succesful')
    return redirect('/')


@app.route('/users/<int:user_id>')
def display_user_info(user_id):
    """Shows profile information"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('user_info.html', user=user)


@app.route('/users/edit', methods=["GET", "POST"])
def edit_profile():
    """Allows a user to edit profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.filter_by(id=g.user.id).first()
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        # Check password
        entered_pass = form.password.data
        correct_password = user.check_password(entered_pass)
        if not correct_password:
            flash('Incorrect Password')
            return redirect('/users/edit')

        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        try:
            user.edit_user(username, first_name, last_name, email)
            flash('user edited')
            return redirect(f'/users/{user.id}')
        except:
            db.session.rollback()
            flash('user not edited')
            return redirect(f'/users/{user.id}')

    return render_template('edit.html', user=user, form=form)


@app.route('/users/password', methods=["GET", "POST"])
def change_password():
    """Allows users to change their password"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.filter_by(id=g.user.id).first()
    form = ChangePwdForm()

    if form.validate_on_submit():
        old_password = form.old_password.data
        correct_password = user.check_password(old_password)

        if not correct_password:
            flash('Incorrect Password')
            return redirect('/users/password')

        new_password = form.new_password.data

        try:
            user.change_password(new_password)
            flash('Password Changed')
            return redirect(f'/users/{user.id}')
        except:
            db.session.rollback()
            flash('Password Not changed (error)')
            return redirect(f'/users/{user.id}')

    return render_template('password.html', user=user, form=form)


@app.route('/users/delete')
def delete_user():
    """Allows user to delete their account"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/register")


# Search Routes ########################################

@app.route('/search', methods=["GET", "POST"])
def find_hikes():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SearchForm()
    form.radius.choices = [(5000, 3), (8000, 5), (12500, 8),
                           (16000, 10), (24000, 15), (32000, 20)]

    if request.method == "GET":
        form.radius.default = int(float(request.args.get('radius', 5000)))
        form.process()
        form.address.data = request.args.get('address', '')

    if form.validate_on_submit():
        address = form.address.data
        coords = Search.get_coords(address)
        radius = form.radius.data

        raw_results = Search.get_hikes(coords, radius)
        hikes = Search.show_search_results(raw_results)

        for hike in hikes:
            hike_search = Search(user_id=g.user.id, name=hike.name, address=address,
                                 radius=radius, place_id=hike.place_id, timestamp=None)
            try:
                db.session.add(hike_search)
                db.session.commit()

            except:
                db.session.rollback()

        return render_template('search.html', form=form, hikes=hikes, address=address, coords=coords)

    return render_template('search.html', form=form)


@app.route('/search/details', methods=["POST"])
def return_search_details():
    """Receives request from front-end"""

    destination_id = request.json['destination_id']
    origin_address = request.json['origin_address']

    directions = Search.get_directions(origin_address, destination_id)

    return jsonify(directions)


@app.route('/search/past', methods=["GET", "POST"])
def get_past_searches():
    """Retrieves past searches for a user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    past_searches = Search.query.filter_by(user_id=g.user.id).limit(1000).all()
    
    sorted_searches = Search.sort_searches(past_searches)

    return render_template('past.html', past_searches=past_searches, sorted_searches=sorted_searches)


@app.route('/search/forecast', methods=["POST"])
def return_forecast():
    """Receives coords and returns 5-day forecast"""

    coords_str = request.json['coords']
    coords = eval(coords_str)
    forecast = Search.get_forecast(coords)

    return jsonify(forecast)
