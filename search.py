from operator import add
import requests
from secret import weather_key, google_key
from user import db
from datetime import datetime
import pprint
# pprint needed for parsing/debugging json responses


FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
GOOGLE_BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/output"
GOOGLE_GEOCODE = 'https://maps.googleapis.com/maps/api/geocode/json?'



class Search(db.Model):
    "Search Model"

    __tablename__ = 'map_searches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    radius = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    @classmethod
    def get_coords(cls, address):
        """Given an address, returns the coords"""

        res = requests.get(f"{GOOGLE_GEOCODE}", params={
            'key': google_key,
            'address': address
        })

        data = res.json()
        coords = data['results'][0]['geometry']['location']
        # {'lat': 42.3292493, 'lng': -71.352353} example coords

        return coords


    @classmethod
    def get_forecast(cls, coords):
        """Given coords, returns forecast"""

        res = requests.get(f"{FORECAST_BASE_URL}", params={
            'lat': coords['lat'],
            'lon': coords['lng'],
            'appid': weather_key
        })

        return res.json()

    @classmethod
    def get_hikes(cls, coords, radius):
        """Given coords, returns hikes within a given radius"""

        google_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        # {'lat': 42.328806, 'lng': -71.352312}
        # coords = '42.3376669449116, -71.33793080449101'
        test_coords = f'{coords["lat"]},{coords["lng"]}'
        params = {
            'location': test_coords,
            'radius': radius,
            'keyword': 'hike',
            'key': google_key}

        response = requests.get(google_url, params=params)
        return response.json()

    @classmethod
    def show_search_results(cls, raw_search_results):
        """Takes in json and returns instances of Result Class"""
        results = raw_search_results['results']

        search_list = []

        for result in results:
            name = result['name']
            address = result['vicinity']
            place_id = result['place_id']
            # lat = result['geometry']['location']['lat']
            # lng = result['geometry']['location']['lng']

            search_obj = Search(name=name, address=address, place_id=place_id)
            search_list.append(search_obj)

        return search_list

    @classmethod
    def get_directions(csl, origin_address, destination_id):
        """Gives directions to a specific location"""
        direction_url = 'https://maps.googleapis.com/maps/api/directions/json'

        # place_id must be prefaced with place_id: <id here>
        # 'destination': f'place_id:{destination_id}'
        # Both must be exactly this format or won't work
        params = {
            'origin': origin_address,
            'destination': f'place_id:{destination_id}',
            'key': google_key
        }

        response = requests.get(direction_url, params)
        return response.json()

    @classmethod
    def sort_searches(csl, past_searches):
        """Returns all unique past searches for a given user"""

        sorted_searches = []
        for count, search in enumerate(past_searches):
        
            search.timestamp_mod = str(search.timestamp).split(' ')[0]
            # Changes format of timestamp without altering original timestamp
            if count == 0:
                sorted_searches.append(search)
            if count > 0 and (search.address != past_searches[count-1].address or search.radius != past_searches[count-1].radius):
                # ensures returning only unique searches.
                sorted_searches.append(search)

        return sorted_searches  

    def __repr__(self):
        return f"<Search #{self.id}: user_id: {self.user_id}, name: {self.name}, address: {self.address}, radius: {self.radius}, place_id: {self.place_id}, timestamp: {self.timestamp}>"       
