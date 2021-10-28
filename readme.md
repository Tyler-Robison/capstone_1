# Hike Finder

A website for finding local hikes


## The Project
This is my first capstone project for the Springboard Software Engineering Bootcamp.

### Project Details

* Hike Finder allows users to enter an address anywhere in the world along with a search radius and receive back up to 20 hikes found within that radius.
  * Most users will enter their own address but if they are planning to go somewhere they can enter a distant address. 

* For a given hike, users can view directions from the entered address to the hike. If the given address was a city name the directions will start from the geographic center of the city. 
  * A list of hikes wouldn't be very useful without knowing how to get there.

* Additionally, a 5-day weather forecast for the area can be viewed. 
  * Users will also want to know the weather.

* All unique user searches are saved and can be made again with the same or modified search parameters. 
  * Users may want to repeat searches from previous days and they might not remember the address or search radius they entered. 

### Site Navigation

* Upon visiting the site, users will be redirected to the registration page where they can make an account. If the user already has an account they can go to the login page instead. 

* Upon succesful login, users can view/edit their profile information, search for hikes or view/repeat past searches they have made.  

* Admin users have the additional ability to delete other user accounts. 

### APIs used

* Google Maps API was used for finding hikes within a given radius and providing directions to those hikes. 

* The Weather API from OpenWeather was used for 5-day forecast.

### Languages and Tools used

* HTML/Jinja for dynamic HTML templating

* CSS/bootstrap 5.0 for visual design

* Javascript/Axios for front-end logic/requests

* Python/Flask for back-end logic
  * Flask WTForms used for creating forms and validating CSRF tokens
  * Flask Bcrypt used for password encryption and validation 

* PostgreSQL for relational database
  * SQLAlchemy - Python ORM for database

* Additional requirements listed in requirements.txt

* If attempting to run this yourself you'll need to create a secret.py for API key storage, that file is essential and not stored on GitHub.


