"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py



import os
from unittest import TestCase
from sqlalchemy import exc
from user import db, User

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


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res    

    def test_user_model(self):
        """Does basic model work?"""

        # User should have attrs given to it at registration
        self.assertEqual(self.u1.username, 'testuser1')
        self.assertEqual(self.u1.first_name, 'Tyler')
        self.assertEqual(self.u1.last_name, 'Robison')
        self.assertEqual(self.u1.email, 'email1@test.com')
        self.assertTrue(self.u1.password.startswith('$2b$'))
        self.assertTrue(self.u1.is_admin)

    def test_repr(self):
        """Does repr work?"""

        self.assertEqual(repr(self.u1), '<User #1111, username: testuser1, first_name: Tyler, last_name: Robison, email: email1@test.com, is_admin: True>')    

    def test_edit_user(self):
        """Tests that we can edit a user"""

        self.assertEqual(self.u1.username, 'testuser1')
        self.assertEqual(self.u1.first_name, 'Tyler')
        self.assertEqual(self.u1.last_name, 'Robison')
        self.assertEqual(self.u1.email, 'email1@test.com')

        self.u1.edit_user('new_name', 'Bobby', 'Jones', 'new_email@gmail.com' )   

        self.assertEqual(self.u1.username, 'new_name')
        self.assertEqual(self.u1.email, 'new_email@gmail.com')
        self.assertEqual(self.u1.first_name, 'Bobby')
        self.assertEqual(self.u1.last_name, 'Jones') 

    def test_change_password(self):
        """Tests that we can change password"""

        old_password = self.u1.password
        self.u1.change_password(old_password)
        new_password = self.u1.password
        self.assertNotEqual(old_password, new_password)

        # Check that both are properly hashed
        self.assertTrue(old_password.startswith('$2b$'))
        self.assertTrue(new_password.startswith('$2b$'))


    def test_delete_user(self):
        """Tests that we can delete a user"""

        test_user = User.query.filter_by(id=1111).first()
        self.assertEqual(test_user.username, 'testuser1')
        self.assertEqual(len(User.query.all()), 2)

        db.session.delete(test_user)
        db.session.commit()
        
        self.assertEqual(User.query.filter_by(id=1111).first(), None)  
        self.assertEqual(len(User.query.all()), 1)  

    def test_authenticate(self):
        """Tests that we can authenticate a user"""

        user = User.authenticate(self.u1.username, 'password1')
        self.assertIsInstance(user, User)   


    #test failure cases ###################################### 

    def test_auth_username_fail(self):
        """Tests that authentication fails if bad username is provided"""

        user = User.authenticate('wrong_username', 'password1')
        self.assertFalse(user)

    def test_auth_password_fail(self):
        """Tests that authentication fails if bad password is provided"""

        user = User.authenticate(self.u1.username, 'wrong_password')
        self.assertFalse(user)    

    def test_no_password(self):
        """user attempts registration without a password"""
        self.assertRaises(ValueError, User.register, 'username3', None, 'Sarah', 'Parker', 'email3@email.com', False)

    def test_no_email(self):
        """user attempts registration without email"""
        new_user = User.register('username3', 'password3', 'Sarah', 'Parker', None, False)
        db.session.add(new_user)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_no_username(self):
        """user attempts registration without username"""    
        new_user = User.register(None, 'password3', 'Sarah', 'Parker', 'email3@email.com', False)
        db.session.add(new_user)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_non_unique_username(self):
        """user attempts registration without unique username"""

        new_user = User.register('testuser1', 'password3', 'Sarah', 'Parker', 'email3@email.com', False)
        db.session.add(new_user)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_non_unique_email(self):
        """user attempts registration without unique email"""

        new_user = User.register('testuser3', 'password3', 'Sarah', 'Parker', 'email1@test.com', False)
        db.session.add(new_user)
        self.assertRaises(exc.IntegrityError, db.session.commit)


            

