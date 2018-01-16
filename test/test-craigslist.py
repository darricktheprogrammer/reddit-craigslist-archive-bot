import unittest

from archivebot import craigslist
from archivebot.craigslist import InvalidIdException


class TestUrlScraper(unittest.TestCase):
	"""
	There will usually only be one craigslist url, but because there can be
	more than one, `scrape_url` always returns a list.
	"""
	def test_IdFromUrl_GivenUrl_ReturnsId(self):
		url = 'https://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		self.assertEqual(craigslist.id_from_url(url), '6451661128')

	def test_IdFromUrl_GivenInvalidUrl_ThrowsError(self):
		url = 'https://indianapolis.craigslist.org/bar/d/bears/645166112.html'
		with self.assertRaises(InvalidIdException):
			craigslist.id_from_url(url)


if __name__ == '__main__':
	unittest.main()
