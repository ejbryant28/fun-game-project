from model import *

from sqlalchemy import func
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

def videos_by_video_challenge(challenge_name):
    
    return db.session.query(Video).join(VideoChallenge).filter(VideoChallenge.challenge_name == challenge_name).order_by(Video.date_uploaded.desc())

def video_by_challenge_name_user_id(challenge_name, user_id):

    return db.session.query(Video).join(VideoChallenge).filter(Video.user_id==user_id, VideoChallenge.challenge_name==challenge_name)

#Tags
######################################################################################################################################


#Challenges
######################################################################################################################################


def challenges_by_name(challenge_name):

    return Challenge.query.filter(Challenge.challenge_name==challenge_name)

#Points Given
######################################################################################################################################

def social_points(user_id):

    return PointGiven.query.filter(PointGiven.user_id == user_id)


def points_videos_by_user_id(user_id):

    return db.session.query(PointGiven).join(Video).filter(Video.user_id ==user_id)

def points_userid_grouped(user_id):

    return points_videos_by_user_id(user_id).group_by(PointGiven.point_category, PointGiven.point_giving_id)

def points_by_user_id_category(user_id, category):

    return UserLevelCategory.query.filter(UserLevelCategory.user_id == user_id, UserLevelCategory.point_category == category)
def newest_points(user_id, last_updated):
    
    return db.session.query(PointGiven).join(Video).filter(Video.user_id ==user_id, PointGiven.time_given > last_updated)

#PointCategory
######################################################################################################################################



#VideoPointTotals
######################################################################################################################################
def video_points_by_video_id(video_id):

    return VideoPointTotals.query.filter(VideoPointTotals.video_id==video_id)

def video_point_totals_by_video_id_point_category(video_id, point_category):

    return VideoPointTotals.query.filter(VideoPointTotals.video_id == video_id, VideoPointTotals.point_category==point_category)


def video_point_totals_by_user_id_grouped_category(user_id):

    return db.session.execute("SELECT video_point_totals.point_category, sum(video_point_totals.total_points) FROM video_point_totals JOIN videos USING (video_id) WHERE videos.user_id = {} GROUP BY video_point_totals.point_category".format(user_id))


#level requirements
######################################################################################################################################

def level_category_current_point(category, total_points):
    return CategoryLevelPoints.query.filter(CategoryLevelPoints.point_category == category, CategoryLevelPoints.points_required <= total_points).order_by(CategoryLevelPoints.level_number.desc())

#UserLevelCategory
######################################################################################################################################

def overall_point_total(user_id):

    base_query = db.session.query(func.sum(UserLevelCategory.user_total_points))
    points = base_query.filter(UserLevelCategory.user_id==user_id).first()
    return points[0]





