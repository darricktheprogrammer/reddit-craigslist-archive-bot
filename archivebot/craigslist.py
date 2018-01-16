import re


class InvalidIdException(Exception):
	pass


def id_from_url(url):
	"""
	Retrieve the Craigslist post id from the url.

	Args:
		url (String): The url from which to extract the id
	Returns:
		String

		A 10-digit post id used for identifying posts
	"""
	match = re.search(r'\d{10}', url)
	if not match:
		msg = 'Could not extract id from {}'.format(url)
		raise InvalidIdException(msg)
	return match.group(0)
