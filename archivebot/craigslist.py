import re

from bs4 import BeautifulSoup
from html2text import html2text

from .custommodels import CraigslistAd
from .errors import InvalidIdException


def scrape_page(html):
	"""
	Scrape the html of a Craigslist posting for desired information.

	Images are only the 600x450 resolution version, not full size. Craigslist
	uses javascript to load the full size image link on rollover of the
	thumbnail. This makes it difficult and slow to retrieve the full size link.

	Args:
		html (String): The html source of the craigslist posting
	Returns:
		BaseCraigslistAd
	"""
	soup = BeautifulSoup(html, 'html.parser')

	# "postinginfo reveal" class gets put in front of "postinginfo", so even
	# though the post id paragraph comes first, it is at index 1 once parsed
	# by BeautifulSoup.
	post_id_paragraph = soup.find_all('p', class_='postinginfo')[1].get_text()
	post_id = re.search(r'\d{10}', post_id_paragraph).group(0)

	url = soup.find('link', rel='canonical').get('href')
	body = soup.find('section', id='postingbody').contents[2:]
	body = '\n'.join([str(line) for line in body]).strip()
	body = html2text(body)

	# Covers all three cases of no image, single image, or multiple images.
	links = [link.get('href') for link in soup.find_all('a')]
	images = [img.get('src') for img in soup.find_all('img')]
	links.extend(images)
	# `set` to remove duplicates.
	# `str` to turn `None` into an iterable so comparison doesn't fail.
	images = list(set([link for link in links if '600x450' in str(link)]))
	return CraigslistAd(post_id, url, body, images=images)


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
