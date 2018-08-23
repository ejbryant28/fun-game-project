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
        name = fake.name().lower()
        # name = name.lower()
        username = name[:5]
        username = username.lower()
        password = 'password'
        email = fake.free_email()

        user = User(name=name, username=username, password=password, email=email)
        db.session.add(user)

    db.session.commit()


def load_videos(n):
    """Give each user n videos, create corresponding files in uploads folder"""

    #get all the users
    users = User.query.all()

    #give each user 5 videos and create those files in uploads folder
    for user in users:

        for i in range(n):
            now = datetime.now()
            filename = name_file() 

            video = Video(user_id = user.user_id, date_uploaded=now, filename=filename)
            db.session.add(video)
            db.session.commit()

            open('./static/uploads/{}'.format(video.filename), "x")


def load_tags():
    """create tags from random list of adjectives"""

    adjectives = ['agreeable', 'ambitious', 'brave', 'calm', 'delightful', 'eager', 'gentle', 'happy', 'jolly', 'kind', 'silly', 'wonderful']

    for adjective in adjectives:

        tag_code = adjective[:5]

        new_tag = Tag(tag_name=adjective)

        db.session.add(new_tag)

    db.session.commit()


def load_videotags():
    """give each video 2 random tags """

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

    categories = ['silliness', 'originality', 'enthusiasm', 'artistry', 'completion', 'social']

    for item in categories:

        new_category = PointCategory(point_category=item)

        db.session.add(new_category)

    db.session.commit()


def load_point_given(n):
    """Give each video n points from a random point category"""

    videos = Video.query.all()
    users = User.query.all()
    now = datetime.now()

    for video in videos:
        for i in range(n):
            #categories come from point categories, excluding social and completion which are calculated seperately.
            categories = ['silliness', 'originality', 'enthusiasm', 'artistry']
            point = choice(categories)

            user = choice(users)

            new_point = PointGiven(video_id=video.video_id, point_category=point, time_given=now, user_id=user.user_id)
        
            db.session.add(new_point)
    db.session.commit()

    #completion points are based on number of videos uploaded
    for user in users:

        videos = videos_by_user_id(user.user_id).all()

        for video in videos:
            new_point = PointGiven(video_id=video.video_id, point_category='completion', time_given=video.date_uploaded, user_id=user.user_id)

            db.session.add(new_point)

    db.session.commit()

def load_challenges():
    """Add challenges from hard coded tuples"""

    challenges_list = [
    ('ostrich', 'Do your best imitation of an ostrich. Running is encouraged.'),
    ('emoji', 'Try to mimic an emoji face'),
    ('hippo', 'Do your best imitation of a hippo. Sound effects are encouraged'),
    ('whale', 'Make whale sounds. Try singing a song.'),
    ('bird', 'Act like your favorite kind of bird. Singing, flying, walking, and squawking are all encouraged.'),
    ('inchworm', 'Move around like an inchworm. Try not to use your arms'),
    ('cat', 'Immitate a silly cat. Bat something around, chase a laser, roll around in catnip... Use your imagination!'),
    ('dog', 'Act like the silliest doggo around. Chase your tail, roll around, do fun tricks, or anything else you can think of.'),
    ('face squash', 'Make silly faces while pushing your face against a window screen, window, or something similar.'),
    ('macarena', 'Do the macarena without the music'),
    ('uncoordinated dance', 'Make a dance where your arms and legs move at very different speeds and/or rythms'),
    ('jellyfish runway', 'Walk down the runway but imagine you have jellyfish legs'),
    ('worm', 'Do the worm poorly'),
    ('upside down songs', 'Sing songs while doing a head or handstand'),
    ('broken shoe dance', 'Do an upbeat dance (like Kazachok or Irish Step Dance) with one high heel and one flat shoe (the shoes can be imaginary).'),
    ('air dancer', 'Immitate an air dancer (those tube things that are in front of car dealerships)'),
    ('fins', 'Put on fins/flippers (for swimming) then walk or run around in them.'),
    ('penguin', 'Run as fast as you can like a penguin.')
    ]


    for challenge in challenges_list:
        new_challenge = Challenge(challenge_name = challenge[0], description=challenge[1])
        db.session.add(new_challenge)
    
    #load 3 random challenges:
    for i in range(3):
        challenge_name = 'challenge_{}'.format(i)
        description = 'This is challenge {}'.format(i)

        new_challenge = Challenge(challenge_name=challenge_name, description=description)
        db.session.add(new_challenge)
    db.session.commit()


def load_video_challenge():
    """Give each video a random challenge"""

    videos = Video.query.all()

    for video in videos:

        challenges = Challenge.query.all()
        challenge = choice(challenges)
        challenges.remove(challenge)

        new_video_challenge = VideoChallenge(video_id=video.video_id, challenge_name=challenge.challenge_name)

        db.session.add(new_video_challenge)

    db.session.commit()


def load_video_point_totals():
    """Each video gets a total points score (from the count of points given) in each point category"""

    videos = Video.query.all()

    for video in videos:

        #get categories so you can go through and add the points for each category available
        categories = point_categories().filter(PointCategory.point_category != 'social').all()

        for category in categories:

            #find the points for a given category on that video
            point_count = PointGiven.query.filter(PointGiven.video_id==video.video_id, PointGiven.point_category==category.point_category).count()

            new_entry = VideoPointTotals(video_id=video.video_id, point_category=category.point_category, total_points=point_count)
            db.session.add(new_entry)

    db.session.commit()

def load_category_level_points():
    """Set the required points for each point_category- right now I'm adding 5 levels each requires 10 points"""

    categories = ['silliness', 'originality', 'enthusiasm', 'social', 'artistry', 'completion']
    initial = [9, 9, 9, 19, 9, 2]

    ##THIS NEEDS TO BE MADE MORE EFFICIENT

    for i in range(len(categories)):

        original_points = initial[i]
        points_required = 0
        point_category = categories[i]

        for n in range(10):
            level_number = n + 1

            print("NEW ENTRY IS", point_category, level_number, points_required)
            new_entry = CategoryLevelPoints(point_category = point_category, level_number=level_number, points_required=points_required)
            db.session.add(new_entry)

            if points_required < 10:
                points_required += 1 + original_points
            else:
                points_required += int(points_required * 0.2) + original_points

    db.session.commit()


def load_user_level():
    """Figure out which level each user is at"""

    users = User.query.all()

    for user in users:
#         #this will return a list of objects 
        point_totals = video_point_totals_by_user_id_grouped_category(user.user_id).fetchall()

        social_points = social_points_count(user.user_id)
        point_totals.append(('social', social_points))

        for entry in point_totals:

            category = entry[0]
            total_points = entry[1]
            level = CategoryLevelPoints.query.filter(CategoryLevelPoints.point_category == category, CategoryLevelPoints.points_required < total_points).order_by(CategoryLevelPoints.level_number.desc()).first()
            level_number = level.level_number
            new_entry = UserLevelCategory(user_id=user.user_id, point_category=category, user_total_points=total_points, level_number=level_number)
            db.session.add(new_entry)
            print("USER ", user.user_id, " HAS LEVEL ", level_number, " IN ", category, " CURRENT POINTS OF ", total_points)
    db.session.commit()


if __name__ == '__main__':
    connect_to_db(app, 'postgres:///project')
    load_users()
    load_videos(5)
    load_tags()
    load_videotags()
    load_pointcategories()
    load_challenges()
    load_video_challenge()
    load_point_given(10)
    load_video_point_totals()
    load_category_level_points()
    load_user_level()




