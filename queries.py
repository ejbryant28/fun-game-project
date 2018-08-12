from model import *
## All the queries used in various other files##


#User queries
######################################################################################################################################

def user_by_user_id(user_id):

	return User.query.filter(User.user_id==user_id)

def user_by_username(username):

	return User.query.filter(User.username==username)

#Video queries
######################################################################################################################################

def videos_by_date():

	return Video.query.order_by(Video.date_uploaded.desc())

def videos_by_user_id(user_id):

	return Video.query.filter(Video.user_id==user_id).order_by(Video.video_id.desc())

def videos_by_filename(filename):

	return Video.query.filter(Video.filename == filename)

#Tags
######################################################################################################################################

def tags():

	return Tag.query

######################################################################################################################################

def challenges():

	return Challenge.query