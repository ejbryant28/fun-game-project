from random import choice
from queries import *
from datetime import datetime

def words_list():
    """pull in all words from words.txt and create a set"""

    filename = None

    with open('words.txt') as f:
        words = f.readlines()
        words = [x.strip() for x in words]
    return words


def name_file(file_ext='mp4'):
    """choose a random word from words_list, make sure there isn't another file with same name, return filename 
    >>> new_file = name_file()
    >>> test = Video.query.filter(Video.filename==new_file).first()
    >>> test == None
    True
    """

    words = words_list()
    filename = None
    while filename == None:
        attempt = choice(words)
        if videos_by_filename(attempt).first() == None:
            print("I found a name")
            filename = attempt + '.' + file_ext
        else:
            print("OOPS. Tried to name a file the same thing")
    
    return filename

def cat_vid_id_tups(points_given):
    """Create tuples of categories and video ids from point_given objects"""

    given_tups = []
    for point in points_given:
        given_tup = (point.point_category, point.video_id)
        given_tups.append(given_tup)

    return given_tups

def update_tables(new_points, user_id):

    flash_messages = []
    #add each one to the video_point_totals table
    for point in new_points:
        #first find the video in the video_point_total table
        video_id = point.video_id
        category = point.point_category

        #update user level table accordingly
        user_level = UserLevelCategory.query.filter(UserLevelCategory.user_id==user_id, UserLevelCategory.point_category==category).first()
        user_level.user_total_points +=1
        flash_messages.append("You got a new {} point for video {}!".format(category, video_id))

        #reset time updated to be now
        now = datetime.now()
        user_level.last_updated = now

        #check to see if they leveled up
        new_level = level_category_current_point(category, user_level.user_total_points).first()

        if new_level.level_number > user_level.level_number:
            flash_messages.append("YOU LEVELED UP IN {}".format(category))
            user_level.level_number = new_level.level_number
        db.session.commit()

    return flash_messages

def make_chart_core_lst(category, user_id):
    all_points = db.session.query(PointGiven).join(Video).filter(Video.user_id ==user_id, PointGiven.point_category==category).order_by(PointGiven.time_given.asc()).all()

    points_lst = []
    point_num = 1
    for point in all_points:

        points_lst.append((point.time_given, 1 + point_num/10))
        point_num += 1

    return points_lst

def make_chart_soc(user_id):

    social_points = PointGiven.query.filter(PointGiven.user_id == user_id).order_by(PointGiven.time_given.asc()).all()

    points_lst = []
    point_num = 1
    for point in social_points:

        points_lst.append((point.time_given, 1 + point_num/22))

        point_num+=1

    return points_lst

def make_chart_comp(user_id):

    completion = Video.query.filter(Video.user_id==user_id).order_by(Video.date_uploaded.asc()).all()
    com_point = 1
    points_lst = []

    for video in completion:

        # if 'completion' in points_dict:
        #     points_dict['completion'].append((video.date_uploaded, 1 + com_point/3))
        # else:
        points_lst.append((video.date_uploaded, 1 + com_point/3))
        com_point+=1
    return points_lst

if __name__ == "__main__":
    import doctest

    print()
    result = doctest.testmod()
    if not result.failed:
        print("ALL TESTS PASSED. GOOD WORK!")
    print()
