from flask_sqlalchemy import SQLAlchemy

from model import *

from server import app, upload_file

from faker import Faker

from datetime import datetime

from helper_functions import name_file, make_points_dictionary

from random import choice

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


def load_videos():

    #get all the users
    users = User.query.all()

    #give each user 5 videos and create those files in uploads folder
    for user in users:
        now = datetime.now()
        
        filename_1 = name_file() 
        filename_2 = name_file()

        video_1 = Video(user_id = user.user_id, date_uploaded=now, filename=filename_1)
        video_2 = Video(user_id = user.user_id, date_uploaded=now, filename=filename_2)
        db.session.add_all([video_1, video_2])

        open(video_1.filename, "a")
        open(video_2.filename, "a")

    db.session.commit()

def load_tags():
    """create tags from random list of adjectives"""

    adjectives = ['agreeable', 'ambitious', 'brave', 'calm', 'delightful', 'eager', 'gentle', 'happy', 'jolly', 'kind', 'silly', 'wonderful']

    for adjective in adjectives:

        tag_code = adjective[:5]

        new_tag = Tag(tag_name=adjective)

        db.session.add(new_tag)

    db.session.commit()

def load_videotags():

    videos = Video.query.all()
    tags = Tag.query.all()

    for video in videos:

        choice_1 = choice(tags)
        choice_2 = choice(tags)

        new_tag_1 = VideoTag(video_id=video.video_id, tag_name=choice_1.tag_name)
        new_tag_2 = VideoTag(video_id=video.video_id, tag_name=choice_2.tag_name)

        db.session.add_all([new_tag_1, new_tag_2])

    db.session.commit()

def load_pointcategories():
    """Create point categories from a list"""

    categories = ['silliness', 'originality', 'enthusiasm', 'social', 'grace', 'completion']

    for item in categories:

        new_category = PointCategory(point_category=item)

        db.session.add(new_category)

    db.session.commit()


def load_point_given():
    """Give each video 50 points from a random point category"""

    videos = Video.query.all()
    users = User.query.all()

    for video in videos:
        for i in range(50):
            categories = ['silliness', 'originality', 'enthusiasm', 'social', 'grace', 'completion']
            point = choice(categories)

            now = datetime.now()

            user = choice(users)

            new_point = PointGiven(video_id=video.video_id, point_category=point, time_given=now, user_id=user.user_id)
        
            db.session.add(new_point)

    db.session.commit()

def load_challenges():
    """Add three hard coded challenges"""

    challenge1 = Challenge(challenge_name='ostrich', description='do your best imitation of an ostrich. running is encouraged.')
    challenge2 = Challenge(challenge_name='emoji', description='try to mimic an emoji face')
    challenge3 = Challenge(challenge_name='hippo', description='do your best imitation of a hippo. sound effects are encouraged')

    db.session.add_all([challenge1, challenge2, challenge3])
    db.session.commit()


def load_video_challenge():

    videos = Video.query.all()
    challenges = Challenge.query.all()

    for video in videos:
        challenge = choice(challenges)

        new_video_challenge = VideoChallenge(video_id=video.video_id, challenge_name=challenge.challenge_name)

        db.session.add(new_video_challenge)

    db.session.commit()

# def load_point_levels():
#     """Set the required points for each point_category- right now I'm adding 5 levels each requires 10 points"""

#     categories = ['silliness', 'originality', 'enthusiasm', 'social', 'grace', 'completion']

#     levels = [1, 2, 3, 4, 5]

#     for category in categories:

#         for level in levels:

#             new_entry = PointLevel(point_category=category, level_number=level, points_required=500)

#             db.session.add(new_entry)
#     db.session.commit()


def load_user_point_totals():

    videos = Video.query.all()

    for video in videos:

        #get all the points associated with one video
        points = PointGiven.query.filter(PointGiven.video_id==video.video_id).all()

        #make a dictionary of points with keys as categories and values as number of points
        points_dict = {}
        for point in points:
            if point.point_category in points_dict:
                points_dict[point.point_category] +=1
            else:
                points_dict[point.point_category] = 1
        
        
        for category in points_dict:

            new_entry = UserPointTotals(video_id=video.video_id, point_category=category, total_points=points_dict[category])

            db.session.add(new_entry)

    db.session.commit() 




if __name__ == '__main__':
    connect_to_db(app, 'postgres:///project')
    # load_users()
    # load_videos()
    # load_tags()
    # load_videotags()
    # load_pointcategories()
    # load_point_given()
    # load_challenges()
    # load_video_challenge()
    # load_point_levels()
    load_user_point_totals()




