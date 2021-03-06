import unittest

from server import app

from model import User, connect_to_db, db

from seed import seed_test, load_users

import bcrypt

from datetime import datetime

class NoDbNoSession(unittest.TestCase):
    """tests that don't need session or db"""

    def setUp(self):
        """set up test"""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        """"""
        pass

    def test_login_no_session(self):
        """test login page when you're not logged in"""

        result = self.client.get("/login")

        self.assertIn(b'Log In', result.data)
        self.assertIn(b'Create Profile', result.data)
        self.assertNotIn(b'Log Out', result.data)

    def test_create_profile_no_session(self):
        """test create profile page"""

        result = self.client.get("/add-user-form")

        self.assertIn(b'Username', result.data)
        self.assertIn(b'Email', result.data)
        self.assertNotIn(b'Log Out', result.data)


class YesDbNoSession(unittest.TestCase):
    """Tests that need db but no session"""

    def setUp(self): #pragma no cover
        """set up test with db, and users"""

        #set up testing configurations
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        #connect to db
        connect_to_db(app, 'postgres:///testdb')
        db.create_all()

        #add a user to db
        load_users(1)


    def tearDown(self): #pragma no cover
        """close session at end"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


    # def test_login_incorrect_info(self):
    #     """Test login with wrong password and wrong username"""

    #     result = self.client.post('/login-check',
    #                             data={"username": 'wrong',
    #                                 "password": 'wrong'},
    #                             follow_redirects=True)

    #     self.assertIn(b"Ooops. The username you ", result.data)
    #     self.assertIn(b"Log In", result.data)
    #     self.assertNotIn(b"Log Out", result.data)
    #     self.assertNotIn(b"Ooops. Looks like you", result.data)


class EmptyDbNoSession(unittest.TestCase):
    """Tests that need db but no session"""

    def setUp(self):
        """set up test with db, and users"""

        #set up testing configurations
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        #connect to db
        connect_to_db(app, 'postgres:///testdb')
        db.create_all()

    def tearDown(self):
        """close session at end"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def test_create_profile(self):
        """Create profile with new username"""

        form_data = {'name': 'newname', 'username': 'newusername', 'email': 'newemail@email.com', 'password': 'password'}
        result = self.client.post('/add-user', data=form_data, follow_redirects=True)

        self.assertIn(b'Welcome', result.data)
        self.assertIn(b'Log Out', result.data)
        self.assertNotIn(b'Log In', result.data)
        self.assertNotIn(b'Ooops', result.data)



class AlmostEmptyDbandSession(unittest.TestCase):
    """Test pages with a database but no videos or other data in database """
    
    def setUp(self):
        """set up test with session, db, and users"""

        #set up testing configurations
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        #connect to db
        connect_to_db(app, 'postgres:///testdb')
        db.create_all()

        #add a user to db
        hashed = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt())

        user = User(user_id= 1, name='joe', username='joey', password=hashed.decode('utf-8'), email='email@email.com')
        db.session.add(user)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 1

    def tearDown(self):
        """close session at end"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


    def test_homepage(self):
        """Test what you can see in homepage if logged in"""

        result = self.client.get('/',
                                data={},
                                follow_redirects=True)

        self.assertIn(b"Log Out", result.data)
        self.assertNotIn(b"Log In", result.data)
        self.assertNotIn(b"Create Profile", result.data)

    def test_logout(self):
        """Test log out page"""

        result = self.client.get('/logout', data={}, follow_redirects=True)

        self.assertIn(b"Yes, please", result.data)
        self.assertIn(b"No, take", result.data)
        self.assertNotIn(b"Log In", result.data)

    def test_logout_check(self):
        """Test log out check"""

        result = self.client.get('/logout-check', data={}, follow_redirects=True)

        self.assertIn(b"Log In", result.data)
        self.assertNotIn(b"Log Out", result.data)

    def test_profile(self):

        result = self.client.get('/profile', data={}, follow_redirects=True)
        self.assertIn(b"Log Out", result.data)

    def test_login_correct_info(self):
        """Test login with correct info"""

        self.client.get('/logout', data={}, follow_redirects=True)
        # hashed = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt())

        result = self.client.post('/login-check',
                                data={'username': 'joey',
                                    'password': 'password'},
                                follow_redirects=True)
        self.assertIn(b"You&#39;re logged in", result.data)
        self.assertIn(b"Log Out", result.data)
        self.assertNotIn(b"Log In", result.data)
        self.assertNotIn(b"Ooops", result.data)

    def test_before_login(self):
        """test that you are redirected to login if not logged in"""

        self.client.get('/logout-check', data={}, follow_redirects=True)

        result = self.client.get('/challenge',
                                data={},
                                follow_redirects=True)

        self.assertIn(b"Log In", result.data)
        # self.assert


class SeededDbandSession(unittest.TestCase):
    """Test pages with a database but no videos or other data in database """
    
    def setUp(self):
        """set up test with session, db, and users"""

        #set up testing configurations
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        #connect to db
        connect_to_db(app, 'postgres:///testdb')
        db.create_all()


        #seed db with data 
        seed_test()

        #set up session
        with self.client as c:
            with c.session_transaction() as session:
                # session.rollback()
                session['user_id'] = 1

    def tearDown(self):
        """close session at end"""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


    def test_profile(self):
        """Test that profile exists"""

        result = self.client.get('/profile', data={}, follow_redirects=True)

        self.assertIn(b"Details", result.data)
        self.assertIn(b"adjective", result.data)
        self.assertIn(b"Challenge", result.data)
        self.assertIn(b'category', result.data)
        self.assertIn(b'completion', result.data)
        self.assertIn(b'social', result.data)



    def test_video_details(self):
        """Test the video details page"""

        result = self.client.get('/video-upload/filename_1.mp4', data = {}, follow_redirects=True)

        # self.assertIn(b'Added', result.data)
        self.assertIn(b'adjective', result.data)
        self.assertIn(b'category', result.data)
        self.assertIn(b'1', result.data)

    def test_video_upload_form(self):
        """Test the video upload form"""

        result = self.client.get('/video-upload/challenge/challenge', data = {}, follow_redirects=True)
        # result = self.client.get('/video-upload/', data = {}, follow_redirects=True)


        self.assertIn(b'challenge', result.data)
        self.assertIn(b'description', result.data)

        self.assertIn(b'Choose some tags', result.data)


    def test_point_giving(self):
        """Test one users giving another user a point"""

        info = {'cat_vid_id': 'category_1'}
        result = self.client.post('/add_point', data=info, follow_redirects=True)

        self.assertIn(b'2', result.data)

    def test_social_points_update(self):

        info = {'cat_vid_id': 'category_1'}
        self.client.post('/add_point', data=info, follow_redirects=True)

        result = self.client.get('/profile', data={}, follow_redirects=True)

        self.assertIn(b"level 1 | total: 1", result.data)

    def test_point_flashing(self):
        """Tests that if a user gets a point while logged out, they get a flash message when they log back in"""

        #first (logged in as user 1) give a point to user 2
        info = {'cat_vid_id': 'category_2'}
        self.client.post('/add_point', data=info, follow_redirects=True)

        #log user 1 out
        self.client.get('/logout-check', data={}, follow_redirects=True)


        # log in  as user_2 and check for flash message
        login_info_1 = {'username': 'username_2', 'password':'password'}
        result_1 = self.client.post('/login-check', data=login_info_1, follow_redirects=True)
        self.assertIn(b"You got a new category point", result_1.data)






######################################################################################################################################
if __name__ == "__main__":

    unittest.main()


    