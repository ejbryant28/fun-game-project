from random import choice
from queries import videos_by_filename

def words_list():
    """pull in all words from words.txt and create a set"""

    filename = None

    with open('words.txt') as f:
        words = f.readlines()
        words = [x.strip() for x in words]
    return words


def name_file(file_ext='mp4'):
    """choose a random word from words_list, make sure there isn't another file with same name, return filename """

    words = words_list()
    filename = None
    while filename == None:
        attempt = choice(words)
        if videos_by_filename(attempt).first() == None:
            print("GOT ONE")
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
