"""Search View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_search_views.py



import os
from unittest import TestCase

from user import db, User
from search import Search

os.environ['DATABASE_URL'] = "postgresql:///weather_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class SearchViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        u1 = User.register("testuser1", "password1", "Tyler",
                           "Robison", "email1@test.com", True)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register("testuser2", "password2", "Jane",
                           "Smith", "email2@test.com", False)
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
        s2 = Search.query.get(sid2)

        self.s1 = s1
        self.sid1 = sid1

        self.s2 = s2
        self.sid2 = sid2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_find_hikes(self):
        """"Can we get hikes"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })

            resp = c.post('/search', data={
                'address': '101 loker st',
                'radius': 5000
            })

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Get Directions', html)
            self.assertIn('5 day forecast', html)


    def test_return_directions(self):
        """When receiving data from front-end can we display directions"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })

            resp = c.post('/search', data={
                'address': '101 loker st',
                'radius': 5000
            })

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Get Directions', html)
            self.assertIn('5 day forecast', html)

      
            json_resp = c.post('/search/details', json={
                'origin_address': '101 loker st',
                'destination_id': 'ChIJVxwHDsyF44kR2sqNCPwrBYk'
            })

            html = json_resp.get_data(as_text=True)
            self.assertIn('place_id', html)
            # We are getting back correct json response
            
    def test_return_forecast(self):
        """When receiving data from front-end can we display forecast"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })

            resp = c.post('/search', data={
                'address': '101 loker st',
                'radius': 5000
            })

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Get Directions', html)
            self.assertIn('5 day forecast', html)

            json_resp = c.post('/search/forecast', json={
                'coords':"{'lat': 42.3292493, 'lng': -71.352353}"
            })

            html = json_resp.get_data(as_text=True)
            self.assertIn('city', html)




    def test_past_searches(self):
        """Can we see past user searches in HTML"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })

            resp = c.get('/search/past')

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('hike_address', html)
            # self.assertIn('5 day forecast', html)

    def test_search_again(self):
        """Do forms autofill when searching again"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })

            resp = c.get('/search?address=101%20loker%20st&radius=5000')

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('101 loker', html)
            self.assertIn('selected value="5000"', html)
