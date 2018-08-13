from random import choice

from queries import points_by_user_id

def words_list():
    """pull in all words from words.txt and create a set"""
    
    with open('words.txt') as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    return content


def name_file(file_ext='mp4'):

    words = words_list()
    name = choice(words) + '.' + file_ext
    return name

def make_points_dictionary(user_id):

    points = points_by_user_id(user_id)

    points_dict = {}
    for point in points:
        if point.point_category in points_dict:
            points_dict[point.point_category] +=1
        else:
            points_dict[point.point_category] = 1

    return points_dict