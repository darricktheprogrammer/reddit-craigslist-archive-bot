import re


def extract_urls(post):
	"""
	Extract any urls that point to a craigslist post from the text of a post.

	Args:
		txt (String): The text of a post or submission
	Returns:
		List

		0 or more craigslist post urls
	"""
	return re.findall(r'[\w\.:/]+?craigslist.org.+?.*?\.html', post)
