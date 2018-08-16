from flask_sqlalchemy import SQLAlchemy

from model import *

from server import app, upload_file

from faker import Faker

from datetime import datetime

from helper_functions import name_file

from random import choice

from queries import * 

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
    # users= users().all()

    #give each user 5 videos and create those files in uploads folder
    for user in users:

        for i in range(5):
            now = datetime.now()
        
            filename = name_file() 

            video = Video(user_id = user.user_id, date_uploaded=now, filename=filename)

            db.session.add(video)

            open(video.filename, "a")

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
    # videos = videos().all()
    tags = Tag.query.all()
    # tags = tags().all()

    for video in videos:

        choice_1 = choice(tags)
        choice_2 = choice(tags)

        new_tag_1 = VideoTag(video_id=video.video_id, tag_name=choice_1.tag_name)
        new_tag_2 = VideoTag(video_id=video.video_id, tag_name=choice_2.tag_name)

        db.session.add_all([new_tag_1, new_tag_2])

    db.session.commit()

def load_pointcategories():
    """Create point categories from a list"""

    categories = ['silliness', 'originality', 'enthusiasm', 'social', 'style', 'completion']

    for item in categories:

        new_category = PointCategory(point_category=item)

        db.session.add(new_category)

    db.session.commit()


def load_point_given():
    """Give each video 50 points from a random point category"""

    videos = Video.query.all()
    # videos = videos().all()
    users = User.query.all()
    # users = users().all()
    now = datetime.now()

    for video in videos:
        for i in range(10):
            #categories come from point categories, excluding social and completion which are calculated seperately.
            categories = ['silliness', 'originality', 'enthusiasm', 'style']
            point = choice(categories)

            user = choice(users)

            new_point = PointGiven(video_id=video.video_id, point_category=point, time_given=now, user_id=user.user_id)
        
            db.session.add(new_point)
    db.session.commit()

    #completion points are based on number of videos uploaded
    for user in users:

        # videos = Video.query.filter(Video.user_id==user.user_id).all()
        videos = videos_by_user_id(user.user_id).all()

        for video in videos:
            new_point = PointGiven(video_id=video.video_id, point_category='completion', time_given=video.date_uploaded, user_id=user.user_id)

            db.session.add(new_point)

    #social points are calculated based on how many points a user has given other people
    for user in users:
        # points_given = PointGiven.query.filter(PointGiven.user_id ==user.user_id).all()
        points_given = points_by_user_id(user.user_id).all()

        for point in points_given:

            new_point = PointGiven(video_id=point.video_id, point_category='social', time_given=point.time_given, user_id=user.user_id)

            db.session.add(new_point)

    db.session.commit()

def load_challenges():
    """Add three hard coded challenges"""

    challenge1 = Challenge(challenge_name='ostrich', description='Do your best imitation of an ostrich. Running is encouraged.')
    challenge2 = Challenge(challenge_name='emoji', description='Try to mimic an emoji face')
    challenge3 = Challenge(challenge_name='hippo', description='Do your best imitation of a hippo. Sound effects are encouraged')

    db.session.add_all([challenge1, challenge2, challenge3])

    #load 15 random challenges:
    for i in range(15):
        challenge_name = 'challenge_{}'.format(i)
        description = 'This is challenge {}'.format(i)

        new_challenge = Challenge(challenge_name=challenge_name, description=description)
        db.session.add(new_challenge)
    db.session.commit()


def load_video_challenge():

    videos = Video.query.all()
    # videos = videos().all()
    # challenges = Challenge.query.all()

    for video in videos:

        challenges = Challenge.query.all()
        # challenges = challenges().all()
        challenge = choice(challenges)
        challenges.remove(challenge)

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


def load_video_point_totals():

    videos = Video.query.all()
    # videos = videos().all()

    for video in videos:

        #get categories so you can go through and add the points for each category available
        # categories = PointCategory.query.all()
        categories = point_categories().all()

        for category in categories:

            #find the points for a given category on that video
            point_count = PointGiven.query.filter(PointGiven.video_id==video.video_id, PointGiven.point_category==category.point_category).count()

            new_entry = VideoPointTotals(video_id=video.video_id, user_id=video.user_id, point_category=category.point_category, total_points=point_count)
            db.session.add(new_entry)

    db.session.commit()



if __name__ == '__main__':
    connect_to_db(app, 'postgres:///project')
    load_users()
    load_videos()
    load_tags()
    load_videotags()
    load_pointcategories()
    load_challenges()
    load_video_challenge()
    load_point_given()
    # load_point_levels()
    load_video_point_totals()




