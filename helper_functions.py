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

if __name__ == "__main__":
    import doctest

    print()
    result = doctest.testmod()
    if not result.failed:
        print("ALL TESTS PASSED. GOOD WORK!")
    print()
