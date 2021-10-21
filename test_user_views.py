"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py



import os
from unittest import TestCase

from flask import session
from user import db, connect_db, User
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///weather_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

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


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res    

    def test_registration(self):
        """Tests that we can register a user"""
        with self.client as c:
            resp = c.post("/register", data={
                'username': 'Billy',
                'password': 'billy758',
                'email': 'billy@gmail.com',
                'first_name': 'Billy',
                'last_name': 'Jones'
            })

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/search')

            new_user = User.query.filter_by(username='Billy').first()
            self.assertEqual(new_user.username, 'Billy')
            self.assertTrue(new_user.password.startswith('$2b$'))
            self.assertEqual(new_user.email, 'billy@gmail.com')
            self.assertEqual(new_user.first_name, 'Billy')
            self.assertEqual(new_user.last_name, 'Jones')
            self.assertFalse(new_user.is_admin)
            self.assertEqual(session[CURR_USER_KEY], new_user.id)    

    def test_registration_redirect(self):
        """After registration are we redirected to search page"""
        with self.client as c:
            resp = c.post("/register", data={
                'username': 'Billy',
                'password': 'billy758',
                'email': 'billy@gmail.com',
                'first_name': 'Billy',
                'last_name': 'Jones'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Hike Finder', html)

    def test_login(self):
        """Tests that we can login a user"""

        with self.client as c:
            resp = c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/search')

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id)  

    def test_login_redirect(self):
        """After login are we redirected to search"""

        with self.client as c:
            resp = c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            }, follow_redirects=True)  

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Hike Finder', html)          

    def test_logout(self):
        """Tests that a user can logout"""

        with self.client as c:
            resp = c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id)

            resp = c.get('logout')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/')

            user = User.query.filter_by(username='testuser').first()
            self.assertEqual(session.get(CURR_USER_KEY), None)

    def test_logout_redirect(self):
        """After logout are we redirected to homepage"""

        with self.client as c:
            resp = c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id)

            resp = c.get('/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Logout Succesful', html)    

    def test_register_bad_username(self):
        """Tests that we can't register with a non-unique username"""

        with self.client as c:
            resp = c.post("/register", data={
                'username': 'testuser1',
                'password': 'billy758',
                'email': 'billy@gmail.com',
                'first_name': 'Billy',
                'last_name': 'Jones'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)   

    def test_register_bad_email(self):
        """Tests that we can't register with a non-unique email"""

        with self.client as c:
            resp = c.post("/register", data={
                'username': 'Billy',
                'password': 'billy758',
                'email': 'email1@test.com',
                'first_name': 'Billy',
                'last_name': 'Jones'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)       

    def test_register_bad_password(self):
        """Tests that we can't register with a password less than 6 characters"""

        with self.client as c:
            resp = c.post("/register", data={
                'username': 'Billy',
                'password': 'billy',
                'email': 'email1@test.com',
                'first_name': 'Billy',
                'last_name': 'Jones'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Field must be at least 6 characters long', html)            

    def test_login_bad_credentials(self):
        """Tests that we cant login with bad credentials"""

        with self.client as c:
            resp = c.post("/login", data={
                'username': '123456',
                'password': 'abcdef'
            })

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Invalid username/password', html)  

    def test_display_profile(self):
        """While logged in, can we display profile"""     

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })      

            resp = c.get(f'/users/{self.u1.id}')

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('testuser1', html)  
            self.assertIn('Tyler', html) 
            self.assertIn('Robison', html) 
            self.assertIn('email1@test.com', html)

    def test_display_profile_logged_out(self):
        """While logged out, are we prevented from viewing profile info"""      

        with self.client as c:   

            resp = c.get(f'/users/{self.u1.id}', follow_redirects=True)

            self.assertEqual(session.get(CURR_USER_KEY), None)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Access unauthorized', html) 

    def test_edit_profile(self):
        """While logged in, can we edit profile"""

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id) 

            self.assertEqual(user.username, 'testuser1')
            self.assertEqual(user.first_name, 'Tyler')
            self.assertEqual(user.last_name, 'Robison')
            self.assertEqual(user.email, 'email1@test.com')

            resp = c.post('/users/edit', data={
                'username':'new_name',
                'password':'password1',
                'first_name': 'new_first',
                'last_name': 'new_last',
                'email': 'new@gmail.com'
            }, follow_redirects=True) 

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('user edited', html) 

            user = User.query.filter_by(username='new_name').first()
            self.assertEqual(user.username, 'new_name')
            self.assertEqual(user.email, 'new@gmail.com')
            self.assertEqual(user.first_name, 'new_first')
            self.assertEqual(user.last_name, 'new_last')
            

    def test_edit_profile_logged_out(self):
        """Are we prevented from editing profile if not logged in"""

        with self.client as c:

            user = User.query.filter_by(username='testuser1').first()

            self.assertEqual(user.username, 'testuser1')
            self.assertEqual(user.first_name, 'Tyler')
            self.assertEqual(user.last_name, 'Robison')
            self.assertEqual(user.email, 'email1@test.com')

            resp = c.post('/users/edit', data={
                'username':'new_name',
                'password':'password1',
                'first_name': 'new_first',
                'last_name': 'new_last',
                'email': 'new@gmail.com'
            }, follow_redirects=True) 

            self.assertEqual(session.get(CURR_USER_KEY), None)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Access unauthorized', html) 

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(user.username, 'testuser1')
            self.assertEqual(user.first_name, 'Tyler')
            self.assertEqual(user.last_name, 'Robison')
            self.assertEqual(user.email, 'email1@test.com')   

    def test_change_password(self):
        """If logged in, can we change our password"""      

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id)    
            old_password = user.password  

            resp = c.post('/users/password', data={
                'new_password': 'new_password1',
                'old_password': 'password1'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Password Changed', html) 

            user = User.query.filter_by(username='testuser1').first()
            new_password = user.password

            self.assertNotEqual(old_password, new_password) 

    def test_change_password_logged_out(self):
        """If logged out, are we prevented from changing password"""

        with self.client as c:

            resp = c.post('/users/password', data={
                'new_password': 'new_password1',
                'old_password': 'password1'
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Access unauthorized', html) 

    def test_change_password_wrong_password(self):
        """If we enter incorrect current password, are we prevented from changing password"""  

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id)    
            old_password = user.password  

            resp = c.post('/users/password', data={
                'new_password': 'new_password1',
                'old_password': 'wrong_password'
            }, follow_redirects=True)      

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Incorrect Password', html) 

            user = User.query.filter_by(username='testuser1').first()
            new_password = user.password  
            self.assertEqual(old_password, new_password)

    def test_edit_profile_wrong_password(self):
        """If we enter incorrect password, are we prevented from editing profile"""        

        with self.client as c:
            c.post("/login", data={
                'username': 'testuser1',
                'password': 'password1'
            })   

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(session[CURR_USER_KEY], user.id) 

            self.assertEqual(user.username, 'testuser1')
            self.assertEqual(user.first_name, 'Tyler')
            self.assertEqual(user.last_name, 'Robison')
            self.assertEqual(user.email, 'email1@test.com')

            resp = c.post('/users/edit', data={
                'username':'new_name',
                'password':'wrong_password',
                'first_name': 'new_first',
                'last_name': 'new_last',
                'email': 'new@gmail.com'
            }, follow_redirects=True) 

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Incorrect Password', html) 

            user = User.query.filter_by(username='testuser1').first()
            self.assertEqual(user.username, 'testuser1')
            self.assertEqual(user.first_name, 'Tyler')
            self.assertEqual(user.last_name, 'Robison')
            self.assertEqual(user.email, 'email1@test.com')

            




            










