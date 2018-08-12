import unittest

from server import app

from model import User, connect_to_db, db

class NoDbNoSession(unittest.TestCase):
	"""tests that don't need session or db"""

	def setUp(self):
		"""set up test"""

		self.client = app.test_client()
		app.config['TESTING'] = True

	def tearDown(self):
		""""""
		pass


# 	def test_homepage_no_session(self):
# 		"""Test what you can see in the homepage if nothing in session"""

# 		result = self.client.get("/")
# 		# self.assertEqual(result.status_code, 200)
# 		self.assertIn(b'Log In', result.data)
# 		self.assertIn(b'Create Profile', result.data)
# 		self.assertNotIn(b'Log out', result.data)

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

	def setUp(self):
		"""set up test with db, and users"""

		#set up testing configurations
		app.config['TESTING'] = True
		app.config['SECRET_KEY'] = 'key'
		self.client = app.test_client()

		#connect to db
		connect_to_db(app, 'postgres:///testdb')
		db.create_all()

		#add a user to db
		user = User(user_id= 1, name='joe', username='joey', password='password', email='email@email.com')
		db.session.add(user)
		db.session.commit()


	def tearDown(self):
		"""close session at end"""

		db.session.close()
		db.drop_all()


	def test_login_correct_info(self):
		"""Test login with correct info"""

		example_user = User.query.get(1)

		result = self.client.post('/login-check',
								data={'username': example_user.username,
									'password': example_user.password},
								follow_redirects=True)
		self.assertIn(b"You&#39;re logged in", result.data)
		self.assertIn(b"Log Out", result.data)
		self.assertNotIn(b"Log In", result.data)
		self.assertNotIn(b"Ooops", result.data)

	def test_login_incorrect_password(self):
		"""Test login with wrong password"""

		example_user = User.query.get(1)

		result = self.client.post('/login-check',
								data={"username": example_user.username,
									"password": 'wrong'},
								follow_redirects=True)

		self.assertIn(b"Ooops. Looks like you", result.data)
		self.assertIn(b"Log In", result.data)
		self.assertNotIn(b"Log Out", result.data)
		self.assertNotIn(b"Ooops. The username", result.data)

	def test_login_incorrect_info(self):
		"""Test login with wrong password and wrong username"""

		result = self.client.post('/login-check',
								data={"username": 'wrong',
									"password": 'wrong'},
								follow_redirects=True)

		self.assertIn(b"Ooops. The username you ", result.data)
		self.assertIn(b"Log In", result.data)
		self.assertNotIn(b"Log Out", result.data)
		self.assertNotIn(b"Ooops. Looks like you", result.data)


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

		db.session.close()
		db.drop_all()

	def test_create_profile(self):
		"""Create profile with new username"""

		test = User.query.first()

		form_data = {'name': 'newname', 'username': 'newusername', 'email': 'newemail@email.com', 'password': 'password'}
		result = self.client.post('/add-user', data=form_data, follow_redirects=True)

		self.assertIn(b'Welcome', result.data)
		self.assertIn(b'Log Out', result.data)
		self.assertNotIn(b'Log In', result.data)
		self.assertNotIn(b'Ooops', result.data)



class YesDbandSession(unittest.TestCase):

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
		user = User(user_id= 1, name='joe', username='joey', password='password', email='email@email.com')
		db.session.add(user)
		db.session.commit()

		with self.client as c:
			with c.session_transaction() as session:
				session['user_id'] = 1


	def tearDown(self):
		"""close session at end"""

		db.session.close()
		db.drop_all()


	def test_homepage(self):
		"""Test what you can see in homepage if logged in"""

		#query database for a username and password
		example_user = User.query.get(1)

		result = self.client.get('/',
								data={},
								follow_redirects=True)

		self.assertIn(b"Log Out", result.data)
		self.assertNotIn(b"Log In", result.data)
		self.assertNotIn(b"Create Profile", result.data)



######################################################################################################################################
if __name__ == "__main__":


    unittest.main()
