from flask_sqlalchemy import SQLAlchemy

from model import User, connect_to_db, db

from server import app

from faker import Faker

fake = Faker()
fake.uri_path(deep=None)


def load_users():
	"""load 10 random users into database"""

	for _ in range(10):
		name = fake.name()
		name = name.lower()

		username = name[:5]
		username = username.lower()

		password = 'password'

		email = fake.free_email()

		user = User(name=name, username=username, password=password, email=email)
		db.session.add(user)

	db.session.commit()


# def load_video():

# 	for i in range(10):

# 		video = fake.file_extension(category=video)



if __name__ == '__main__':
	connect_to_db(app, 'postgres:///project')
	load_users()


