"""User search tests."""

# run these tests like:
#
#    python -m unittest test_search_model.py



import os
from unittest import TestCase
from flask.json import jsonify
from sqlalchemy import exc
from user import db, User
from search import Search

os.environ['DATABASE_URL'] = "postgresql:///weather_test"
from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test methods for User."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.register("testuser1", "password1", "Tyler", "Robison", "email1@test.com", True)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register("testuser2", "password2", "Jane", "Smith", "email2@test.com", False)
        uid2 = 2222
        u2.id = uid2

        db.session.add_all([u1, u2])
        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2
        
        s1 = Search(user_id=u1.id, name='hike_name', address='hike_address',
                                 radius='5000', place_id='place_id1', timestamp=None)
        sid1 = 1111
        s1.id = sid1     

        s2 = Search(user_id=u1.id, name='hike_name2', address='hike_address2',
                                 radius='5000', place_id='place_id1', timestamp=None)
        sid2 = 2222
        s2.id = sid2  

        db.session.add_all([s1, s2])
        db.session.commit()    

        s1 = Search.query.get(sid1)         

        self.s1 = s1
        self.sid1 = sid1       


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res 

    def test_search_model(self):
        """Does basic model work?"""

        # Search should have attrs given to it 
        self.assertEqual(self.s1.name, 'hike_name')
        self.assertEqual(self.s1.address, 'hike_address')
        self.assertEqual(self.s1.radius, 5000)
        self.assertEqual(self.s1.place_id, 'place_id1')

    def test_repr(self):
        """Does repr work?"""
        
        self.assertIn('<Search #1111: user_id: 1111, name: hike_name, address: hike_address, radius: 5000, place_id: place_id1,' , repr(self.s1))

    def test_get_coords(self):
        """Given an address, can we get correct coords"""

        coords = Search.get_coords('101 loker st')  
        self.assertEqual(coords, {'lat': 42.3292493, 'lng': -71.352353})

    def test_get_forecast(self):
        """Given coords, can we get 5-day-forecast"""

        coords = {'lat': 42.3292493, 'lng': -71.352353}
        forecast = Search.get_forecast(coords)       
        self.assertIn('humidity', forecast['list'][0]['main'])

    def test_get_hikes(self):
        """Given coords and radius, can we get hikes"""

        coords = {'lat': 42.3292493, 'lng': -71.352353}
        radius = 5000
        hikes = Search.get_hikes(coords, radius)
        self.assertIn('location', hikes['results'][0]['geometry'])


    def test_show_search_results(self):
        """Given response from API, can we create Search Objects"""
        coords = {'lat': 42.3292493, 'lng': -71.352353}
        radius = 5000

        raw_results = Search.get_hikes(coords, radius)
        hikes = Search.show_search_results(raw_results)
        search_obj = hikes[0]
        self.assertIsInstance(search_obj, Search)

    def test_get_directions(self):
        """Given an address and a destination_id can we get directions"""

        address = '101 loker st'
        dest_id = 'ChIJVxwHDsyF44kR2sqNCPwrBYk'

        directions = Search.get_directions(address, dest_id)
        self.assertIn('place_id', directions['geocoded_waypoints'][0])

    def test_sort_searches(self):
        """Given a user can we sort their searches by unique address/radius"""   

        past_searches = Search.query.filter_by(user_id=self.u1.id).limit(1000).all()
        sorted_searches = Search.sort_searches(past_searches)
        self.assertEqual(len(sorted_searches), 2)

        past_searches = Search.query.filter_by(user_id=self.u2.id).limit(1000).all()
        sorted_searches = Search.sort_searches(past_searches)
        self.assertEqual(len(sorted_searches), 0)

