from flask import Flask, request, render_template, redirect, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from user import db, connect_db, User
from search import Search
from forms import RegisterForm, LoginForm, SearchForm, UserEditForm, ChangePwdForm, PasswordForm
import os

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///weather_app'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "def_key")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

# error handling and setup g.user #####################

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        # g.user is used throughout app to control access to routes
        # and to access information on the currently logged in user
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# User Routes ##########################################

@app.route('/')
def home_page():
    """Redirects to registration page 
    or search page if user already logged in"""

    if g.user:
        flash(f'Welcome Back {g.user.username}')
        return redirect('/search')

    else:
        flash('Please Create Account')
        return redirect('/register')


@app.route('/register', methods=["POST", "GET"])
def register():
    """Allows user to register"""

    if g.user:
        flash('Already Logged in')
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
            # register method converts entered pwd into hashed/salted pwd
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
        flash('Already logged in')
        return redirect('/search')

    form = LoginForm()

    if form.validate_on_submit():
        # ensures POST request and valid CSRF token
        username = form.username.data
        password = form.password.data

        logged_user = User.authenticate(username, password)
        if logged_user:
            session[CURR_USER_KEY] = logged_user.id
            flash(f'Welcome Back {logged_user.username}')
            return redirect('/search')
        else:
            flash("Register if you don't already have account")
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Logs out a user"""

    # No access control on this route, don't need it

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    flash('Logout Succesful')
    return redirect('/login')


@app.route('/users/<int:user_id>')
def display_user_info(user_id):
    """Shows profile information"""

    if not g.user:
        flash("Please Register First")
        return redirect("/register")

    if g.user.id != user_id:
        flash("Access unauthorized, here is your profile")
        return redirect(f"/users/{g.user.id}")    
        # Users can only access profile info for their own account

    user = User.query.get_or_404(user_id)

    return render_template('user_info.html', user=user)


@app.route('/users/edit', methods=["GET", "POST"])
def edit_profile():
    """Allows a user to edit profile"""

    if not g.user:
        flash("Please Register First")
        return redirect("/")

    user = User.query.filter_by(id=g.user.id).first()
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        
        entered_pass = form.password.data
        correct_password = user.check_password(entered_pass)
        # if correct_password = False then entered pwd was wrong
        if not correct_password:
            flash('Incorrect Password')
            return redirect('/users/edit')

        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        try:
            user.edit_user(username, first_name, last_name, email)
            flash('Profile Info Edited')
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
        flash("Please Register First")
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


@app.route('/users/delete', methods=["GET", "POST"])
def delete_user():
    """Allows user to delete their account"""

    if not g.user:
        flash("Please Register First")
        return redirect("/")

    form = PasswordForm()

    if form.validate_on_submit():
        password = form.password.data    

        correct_password = g.user.check_password(password)

        if not correct_password:
            flash('Incorrect Password')
            return redirect('/users/delete')

        if CURR_USER_KEY in session:
            del session[CURR_USER_KEY]

        db.session.delete(g.user)
        db.session.commit()

        flash('Account Deleted')
        return redirect("/register")

    return render_template('delete.html', form=form) 

@app.route('/admin')
def show_admin_panel():
    """Allows admin users to delete other users"""

    users = User.query.all()

    return render_template('admin.html', users=users)    

@app.route('/admin/delete/<int:user_id>', methods=["POST"])   
def admin_delete_user(user_id):
    """Processes an admin deleting another user"""

    if not g.user:
        flash("Please Register First")
        return redirect("/register")

    if g.user.is_admin != True:
        flash("Must be an admin")
        return redirect("/search")

    user = User.query.filter_by(id = user_id).first()

    db.session.delete(user)
    db.session.commit()

    return redirect('/admin')        

   

# Search Routes ########################################

@app.route('/search', methods=["GET", "POST"])
def find_hikes():

    if not g.user:
        flash("Please Register First")
        return redirect("/")

    form = SearchForm()
    form.radius.choices = [(5000, 3), (8000, 5), (12500, 8),
                           (16000, 10), (24000, 15), (32000, 20)]

    if request.method == "GET":
        # This is for searches originating from /search/past route
        # Fills in search info with data from past search
        form.radius.default = int(float(request.args.get('radius', 5000)))
        form.process()
        form.address.data = request.args.get('address', '')

    if form.validate_on_submit():
        address = form.address.data
        coords = Search.get_coords(address)
        radius = form.radius.data

        raw_results = Search.get_hikes(coords, radius)
        # json has to be parsed into the data we want
        # weather.txt contains example json response
        hikes = Search.show_search_results(raw_results)

        for hike in hikes:
            # take data from previous step and create instances of Search object with it
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
def return_directions():
    """Receives request from front-end and responds with hikes"""

    destination_id = request.json['destination_id']
    origin_address = request.json['origin_address']

    directions = Search.get_directions(origin_address, destination_id)

    return jsonify(directions)


@app.route('/search/past', methods=["GET", "POST"])
def get_past_searches():
    """Retrieves past searches for a user"""

    if not g.user:
        flash("Please Register First")
        return redirect("/register")

    past_searches = Search.query.filter_by(user_id=g.user.id).limit(1000).all()
    sorted_searches = Search.sort_searches(past_searches)
    # Gets all searches from user then sorts into unique searches ordered by date

    return render_template('past.html', past_searches=past_searches, sorted_searches=sorted_searches)


@app.route('/search/forecast', methods=["POST"])
def return_forecast():
    """Receives coords from frontend and returns 5-day forecast"""

    coords_str = request.json['coords']
    coords = eval(coords_str)
    forecast = Search.get_forecast(coords)

    return jsonify(forecast)
