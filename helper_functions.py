from random import choice

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
