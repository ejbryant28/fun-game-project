from model import *
## All the queries used in various other files##


#User queries
######################################################################################################################################
def users():
	return User.query

def user_by_user_id(user_id):

	return User.query.filter(User.user_id==user_id)

def user_by_username(username):

	return User.query.filter(User.username==username)

#Video queries
######################################################################################################################################
def videos():
	return Video.query

def videos_by_date():

	return Video.query.order_by(Video.date_uploaded.desc())

def videos_by_user_id(user_id):

	return Video.query.filter(Video.user_id==user_id).order_by(Video.video_id.desc())

def videos_by_filename(filename):

	return Video.query.filter(Video.filename == filename)

def videos_by_video_challenge(challenge_name):
	
	return db.session.query(Video).join(VideoChallenge).filter(VideoChallenge.challenge_name == challenge_name).order_by(Video.date_uploaded.desc())

def video_by_challenge_name_user_id(challenge_name, user_id):

	return db.session.query(Video).join(VideoChallenge).filter(Video.user_id==user_id, VideoChallenge.challenge_name==challenge_name)

#Tags
######################################################################################################################################

def tags():

	return Tag.query

#Challenges
######################################################################################################################################

def challenges():

	return Challenge.query

def challenges_by_name(challenge_name):

	return Challenge.query.filter(Challenge.challenge_name==challenge_name)

#Points Given
######################################################################################################################################

def points_by_user_id(user_id):

	return PointGiven.query.filter(PointGiven.user_id == user_id)

def points_given_by_user_id(user_id):

	return db.session.query(PointGiven).join(Video).filter(Video.user_id == user_id).group_by(PointGiven.point_category, PointGiven.point_giving_id)

def social_points_count(user_id):

	return PointGiven.query.filter(PointGiven.user_id==user_id).count()

#PointCategory
######################################################################################################################################
def point_categories():
	
	return PointCategory.query



#VideoPointTotals
######################################################################################################################################
def video_points_by_video_id(video_id):

	return VideoPointTotals.query.filter(VideoPointTotals.video_id==video_id)

def video_point_totals_by_video_id_point_category(video_id, point_category):

	return VideoPointTotals.query.filter(VideoPointTotals.video_id == video_id, VideoPointTotals.point_category==point_category)


def video_point_totals_by_user_id_grouped_category(user_id):

	return db.session.execute("SELECT video_point_totals.point_category, sum(video_point_totals.total_points) FROM video_point_totals JOIN videos USING (video_id) WHERE videos.user_id = {} GROUP BY video_point_totals.point_category".format(user_id))

def levels_by_user_id_grouped_category(user_id):

	user_totals =  db.session.execute("SELECT video_point_totals.point_category, sum(video_point_totals.total_points), category_level_points.level_number FROM video_point_totals LEFT JOIN videos USING (video_id) LEFT JOIN category_level_points USING (point_category) WHERE videos.user_id = {} GROUP BY video_point_totals.point_category, category_level_points.level_number".format(user_id))
	return user_totals

	# something = db.session.execute("SELECT category_level_points.level_number, video_point_totals.point_category FROM category_level_points JOIN video_point_totals  USING point_category")

	# return something

# levels_by_user_id_grouped_category(1)






